"""
Proctor Engine Module for managing Online Coding Round Assessment workflows.

Stores DSA problems, hidden test cases, candidate submissions, AI baseline references,
and proctoring evaluation reports in structured folder hierarchies.
Orchestrates submission saving, MOSS similarity cross-comparison, Same Bug pattern analysis,
Groq LLM AI forensics, and risk scoring.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ai_detection import GroqClientWrapper, generate_ai_baselines, judge_ai_characteristics
from bug_detection import compare_bug_patterns, extract_bug_pattern
from config import (
    AI_REFERENCES_DIR,
    DATA_DIR,
    PROBLEMS_DIR,
    REPORTS_DIR,
    SUBMISSIONS_DIR,
)
from models import (
    AIDetectionResult,
    BugPattern,
    Problem,
    RiskResult,
    SameBugResult,
    SimilarityResult,
    Submission,
    TestCase,
)
from risk_scoring import calculate_risk_score
from similarity import compare_code_similarity


class OnlineCodingProctorEngine:
    """
    Backend Engine for an Online Coding Assessment System with automated AI multiagent proctoring.
    """

    def __init__(self, data_root: Optional[Path] = None):
        """
        Initializes directory structure and Groq LLM client wrapper.

        Args:
            data_root: Optional custom root directory for assessment data.
        """
        self.data_root = data_root or DATA_DIR
        self.problems_dir = self.data_root / "problems"
        self.submissions_dir = self.data_root / "submissions"
        self.ai_refs_dir = self.data_root / "ai_references"
        self.reports_dir = self.data_root / "reports"

        self._init_directories()
        self.groq_wrapper = GroqClientWrapper()
        self.problems: Dict[str, Problem] = {}
        self.ai_baselines_cache: Dict[str, List[str]] = {}

    def _init_directories(self) -> None:
        """Ensures storage folders exist."""
        for d in [self.problems_dir, self.submissions_dir, self.ai_refs_dir, self.reports_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def register_problem(self, problem: Problem) -> None:
        """
        Registers a DSA problem and persists its schema and test cases to disk.

        Args:
            problem: Problem instance to register.
        """
        self.problems[problem.problem_id] = problem
        prob_folder = self.problems_dir / problem.problem_id
        prob_folder.mkdir(parents=True, exist_ok=True)

        meta_file = prob_folder / "problem.json"
        prob_dict = {
            "problem_id": problem.problem_id,
            "title": problem.title,
            "description": problem.description,
            "entrypoint": problem.entrypoint,
            "test_cases": [
                {
                    "test_id": tc.test_id,
                    "input_data": tc.input_data,
                    "expected_output": tc.expected_output,
                    "is_hidden": tc.is_hidden
                }
                for tc in problem.test_cases
            ]
        }
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(prob_dict, f, indent=2)

    def get_or_generate_ai_baselines(self, problem_id: str) -> List[str]:
        """
        Retrieves cached AI baseline solutions for a problem or generates them via Groq API.

        Args:
            problem_id: Problem ID.

        Returns:
            List of AI reference baseline solution strings.
        """
        if problem_id in self.ai_baselines_cache:
            return self.ai_baselines_cache[problem_id]

        ref_folder = self.ai_refs_dir / problem_id
        ref_folder.mkdir(parents=True, exist_ok=True)
        ref_file = ref_folder / "baselines.json"

        if ref_file.exists():
            try:
                with open(ref_file, "r", encoding="utf-8") as f:
                    baselines = json.load(f)
                    self.ai_baselines_cache[problem_id] = baselines
                    return baselines
            except Exception:
                pass

        problem = self.problems.get(problem_id)
        if not problem:
            return []

        # Generate baselines via Groq LLM API
        baselines = generate_ai_baselines(problem, self.groq_wrapper, num_baselines=3)
        self.ai_baselines_cache[problem_id] = baselines

        with open(ref_file, "w", encoding="utf-8") as f:
            json.dump(baselines, f, indent=2)

        return baselines

    def submit_candidate_code(
        self,
        candidate_id: str,
        problem_id: str,
        code: str
    ) -> Submission:
        """
        Saves candidate submission code to the corresponding problem submission directory.

        Args:
            candidate_id: Candidate identifier.
            problem_id: Problem identifier.
            code: Submitted Python source code.

        Returns:
            Submission object.
        """
        prob_sub_dir = self.submissions_dir / problem_id
        prob_sub_dir.mkdir(parents=True, exist_ok=True)

        submission_id = f"sub_{candidate_id}_{problem_id}"
        code_filepath = prob_sub_dir / f"{candidate_id}.py"

        with open(code_filepath, "w", encoding="utf-8") as f:
            f.write(code)

        submission = Submission(
            submission_id=submission_id,
            candidate_id=candidate_id,
            problem_id=problem_id,
            code=code
        )
        return submission

    def get_all_submissions_for_problem(self, problem_id: str) -> List[Submission]:
        """
        Loads all stored candidate submissions for a specific DSA problem.

        Args:
            problem_id: Problem identifier.

        Returns:
            List of Submission objects.
        """
        prob_sub_dir = self.submissions_dir / problem_id
        if not prob_sub_dir.exists():
            return []

        submissions: List[Submission] = []
        for file in prob_sub_dir.glob("*.py"):
            cand_id = file.stem
            with open(file, "r", encoding="utf-8") as f:
                source = f.read()
            submissions.append(
                Submission(
                    submission_id=f"sub_{cand_id}_{problem_id}",
                    candidate_id=cand_id,
                    problem_id=problem_id,
                    code=source
                )
            )
        return submissions

    def evaluate_submission(
        self,
        candidate_id: str,
        problem_id: str
    ) -> RiskResult:
        """
        Executes complete multiagent proctoring analysis for a candidate submission:
        - MOSS Code Similarity Analysis against all existing candidates and AI baselines.
        - Same Bug Analysis against all existing candidates on hidden test cases.
        - Groq LLM Judge AI-generated code forensics.
        - Weighted Risk Scoring and Flagging.

        Args:
            candidate_id: Candidate ID being evaluated.
            problem_id: Problem ID.

        Returns:
            RiskResult object summarizing analysis findings and risk probability.
        """
        problem = self.problems.get(problem_id)
        if not problem:
            raise ValueError(f"Problem '{problem_id}' is not registered in engine.")

        # Load target candidate submission
        code_filepath = self.submissions_dir / problem_id / f"{candidate_id}.py"
        if not code_filepath.exists():
            raise FileNotFoundError(f"Submission for candidate '{candidate_id}' on problem '{problem_id}' not found.")

        with open(code_filepath, "r", encoding="utf-8") as f:
            target_code = f.read()

        target_sub = Submission(
            submission_id=f"sub_{candidate_id}_{problem_id}",
            candidate_id=candidate_id,
            problem_id=problem_id,
            code=target_code
        )

        # 1. Run target code against hidden test cases
        hidden_tests = [tc for tc in problem.test_cases if tc.is_hidden]
        if not hidden_tests:
            hidden_tests = problem.test_cases

        target_bug_pattern = extract_bug_pattern(
            candidate_id=candidate_id,
            problem_id=problem_id,
            source_code=target_code,
            entrypoint=problem.entrypoint,
            hidden_tests=hidden_tests
        )

        # 2. Fetch or generate AI baselines
        ai_baselines = self.get_or_generate_ai_baselines(problem_id)

        # 3. Cross-compare MOSS Similarity against all other candidates and AI reference code
        all_other_submissions = [
            s for s in self.get_all_submissions_for_problem(problem_id)
            if s.candidate_id != candidate_id
        ]

        max_sim_result: Optional[SimilarityResult] = None
        highest_sim_score = -1.0

        # Compare against peer candidates
        for peer_sub in all_other_submissions:
            sim_res = compare_code_similarity(
                candidate_1_id=candidate_id,
                code1=target_code,
                candidate_2_id=peer_sub.candidate_id,
                code2=peer_sub.code,
                problem_id=problem_id
            )
            if sim_res.similarity_score > highest_sim_score:
                highest_sim_score = sim_res.similarity_score
                max_sim_result = sim_res

        # Compare against AI Baselines
        for i, baseline_code in enumerate(ai_baselines):
            ai_sim_res = compare_code_similarity(
                candidate_1_id=candidate_id,
                code1=target_code,
                candidate_2_id=f"AI_Baseline_{i+1}",
                code2=baseline_code,
                problem_id=problem_id
            )
            if ai_sim_res.similarity_score > highest_sim_score:
                highest_sim_score = ai_sim_res.similarity_score
                max_sim_result = ai_sim_res

        # 4. Cross-compare Same Bug Analysis against all other candidates
        max_bug_result: Optional[SameBugResult] = None
        highest_bug_score = -1.0

        for peer_sub in all_other_submissions:
            peer_pattern = extract_bug_pattern(
                candidate_id=peer_sub.candidate_id,
                problem_id=problem_id,
                source_code=peer_sub.code,
                entrypoint=problem.entrypoint,
                hidden_tests=hidden_tests
            )
            bug_res = compare_bug_patterns(target_bug_pattern, peer_pattern)
            if bug_res.same_bug_score > highest_bug_score:
                highest_bug_score = bug_res.same_bug_score
                max_bug_result = bug_res

        # 5. Execute Groq Judge LLM AI Forensics
        ai_detection_result = judge_ai_characteristics(
            submission_code=target_code,
            problem=problem,
            baselines=ai_baselines,
            groq_wrapper=self.groq_wrapper
        )
        ai_detection_result.candidate_id = candidate_id

        # 6. Calculate Weighted Risk Score
        risk_result = calculate_risk_score(
            candidate_id=candidate_id,
            problem_id=problem_id,
            max_similarity_result=max_sim_result,
            max_bug_result=max_bug_result,
            ai_detection_result=ai_detection_result
        )

        # 7. Persist Evaluation Report to Disk
        self._save_report(risk_result, target_bug_pattern, ai_detection_result)

        return risk_result

    def _save_report(
        self,
        risk_result: RiskResult,
        bug_pattern: BugPattern,
        ai_result: AIDetectionResult
    ) -> None:
        """Saves evaluation report JSON to disk."""
        prob_report_dir = self.reports_dir / risk_result.problem_id
        prob_report_dir.mkdir(parents=True, exist_ok=True)
        report_file = prob_report_dir / f"{risk_result.candidate_id}_report.json"

        report_data = {
            "candidate_id": risk_result.candidate_id,
            "problem_id": risk_result.problem_id,
            "overall_risk": risk_result.overall_risk,
            "is_flagged": risk_result.is_flagged,
            "recommendation": risk_result.recommendation,
            "code_similarity_score": risk_result.code_similarity_score,
            "most_similar_candidate": risk_result.most_similar_candidate,
            "same_bug_score": risk_result.same_bug_score,
            "collusion_partner": risk_result.collusion_partner,
            "ai_probability": risk_result.ai_probability,
            "reasons": risk_result.reasons,
            "hidden_tests_summary": [
                {
                    "test_id": r.test_id,
                    "passed": r.passed,
                    "error_type": r.error_type,
                    "error_message": r.error_message
                }
                for r in bug_pattern.results
            ],
            "ai_detection_details": {
                "confidence": ai_result.confidence,
                "reasons": ai_result.reasons,
                "baseline_matches": ai_result.baseline_matches
            }
        }
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)
