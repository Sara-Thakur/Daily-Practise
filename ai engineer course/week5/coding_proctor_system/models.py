"""
Data models for the Automated Coding Multiagent Proctoring System.

Defines structured schemas for test cases, DSA problems, candidate submissions,
bug pattern signatures, AI detection results, code similarity metrics, and aggregate risk reports.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set


@dataclass
class TestCase:
    """
    Represents a test case for a DSA problem.

    Attributes:
        test_id: Unique identifier for the test case.
        input_data: Input parameters passed to the entrypoint function.
        expected_output: Expected return value from the function.
        is_hidden: Whether this is a hidden test case used for proctoring analysis.
    """

    test_id: str
    input_data: Any
    expected_output: Any
    is_hidden: bool = True


@dataclass
class Problem:
    """
    Represents a DSA coding problem in the online assessment system.

    Attributes:
        problem_id: Unique problem code (e.g., 'prob_1_two_sum').
        title: Human-readable title of the problem.
        description: Problem statement, requirements, and constraints.
        entrypoint: Name of the target Python function to execute.
        test_cases: List of test cases associated with the problem.
    """

    problem_id: str
    title: str
    description: str
    entrypoint: str
    test_cases: List[TestCase] = field(default_factory=list)


@dataclass
class Submission:
    """
    Represents a candidate's code submission for a specific problem.

    Attributes:
        submission_id: Unique ID for the submission file.
        candidate_id: Unique identifier for the candidate/student.
        problem_id: Problem ID being attempted.
        code: Full Python source code submitted by the candidate.
        timestamp: ISO format timestamp of when the submission was recorded.
    """

    submission_id: str
    candidate_id: str
    problem_id: str
    code: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class TestResult:
    """
    Result of executing a single test case against candidate code.

    Attributes:
        test_id: Test case identifier.
        passed: True if actual output matched expected output.
        actual_output: String representation of returned value or error.
        error_type: Normalized error classification (e.g., 'PASSED', 'WRONG_ANSWER', 'IndexError').
        error_message: Optional detailed exception message or traceback.
    """

    test_id: str
    passed: bool
    actual_output: Optional[str] = None
    error_type: str = "PASSED"
    error_message: Optional[str] = None


@dataclass
class BugPattern:
    """
    Captures the behavioral signature of a candidate submission across hidden test cases.

    Attributes:
        candidate_id: Candidate identifier.
        problem_id: Problem identifier.
        results: List of TestResult objects for hidden test cases.
        failure_signature: Tuple representation of failure states for exact matching.
    """

    candidate_id: str
    problem_id: str
    results: List[TestResult] = field(default_factory=list)

    @property
    def failure_signature(self) -> List[Dict[str, Any]]:
        """Extract hashable dictionary signature of test failures."""
        return [
            {
                "test_id": r.test_id,
                "passed": r.passed,
                "error_type": r.error_type,
            }
            for r in self.results
        ]


@dataclass
class SimilarityResult:
    """
    Represents MOSS structural similarity analysis between two code submissions.

    Attributes:
        candidate_1: ID of first candidate.
        candidate_2: ID of second candidate (or 'AI_BASELINE').
        problem_id: Problem identifier.
        similarity_score: Jaccard structural similarity coefficient between 0.0 and 1.0.
        shared_fingerprints_count: Number of matching MOSS fingerprint hashes.
        detected_modifications: List of detected evasion techniques (e.g., variable renaming, dead code).
    """

    candidate_1: str
    candidate_2: str
    problem_id: str
    similarity_score: float
    shared_fingerprints_count: int
    detected_modifications: List[str] = field(default_factory=list)


@dataclass
class SameBugResult:
    """
    Represents Same Bug Analysis between two candidate submissions.

    Attributes:
        candidate_1: ID of first candidate.
        candidate_2: ID of second candidate.
        problem_id: Problem identifier.
        same_bug_score: Similarity of failure patterns (0.0 to 1.0).
        shared_failed_tests: List of test_ids where both candidates failed identically.
        is_collusion_suspect: Flagged if identical failure signatures detected on complex hidden tests.
    """

    candidate_1: str
    candidate_2: str
    problem_id: str
    same_bug_score: float
    shared_failed_tests: List[str] = field(default_factory=list)
    is_collusion_suspect: bool = False


@dataclass
class AIDetectionResult:
    """
    Represents LLM Judge evaluation of AI-generated code characteristics.

    Attributes:
        candidate_id: Candidate identifier.
        problem_id: Problem identifier.
        probability: Score from 0.0 to 1.0 indicating probability code was AI-generated.
        confidence: Judge LLM's self-assessed confidence level (0.0 to 1.0).
        reasons: List of observed AI characteristics (e.g., 'overly perfect formatting', 'canonical structure').
        baseline_matches: Key structural overlap observations with AI baseline solutions.
    """

    candidate_id: str
    problem_id: str
    probability: float
    confidence: float
    reasons: List[str] = field(default_factory=list)
    baseline_matches: List[str] = field(default_factory=list)


@dataclass
class RiskResult:
    """
    Final aggregate risk assessment for a candidate's submission.

    Attributes:
        candidate_id: Candidate identifier.
        problem_id: Problem identifier.
        overall_risk: Weighted risk probability between 0.0 and 1.0.
        is_flagged: True if overall_risk exceeds threshold (e.g., > 0.70).
        code_similarity_score: Maximum code similarity score across other submissions/AI.
        most_similar_candidate: Candidate ID or AI reference with highest similarity.
        same_bug_score: Maximum bug failure pattern similarity across other submissions.
        collusion_partner: Candidate ID sharing identical failure signature.
        ai_probability: AI-generated code probability from LLM judge.
        reasons: Summary of key evidence justifying the risk score.
        recommendation: Suggested proctoring action ('CLEAR', 'MONITOR', 'FLAGGED_FOR_INVESTIGATION').
    """

    candidate_id: str
    problem_id: str
    overall_risk: float
    is_flagged: bool
    code_similarity_score: float
    most_similar_candidate: str
    same_bug_score: float
    collusion_partner: str
    ai_probability: float
    reasons: List[str] = field(default_factory=list)
    recommendation: str = "CLEAR"
