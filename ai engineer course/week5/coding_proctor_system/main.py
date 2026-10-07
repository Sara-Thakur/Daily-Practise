"""
Main CLI Application for the Automated Coding Multiagent Proctoring System.

Runs the sample data generator, initializes the assessment engine, executes
proctoring evaluation pipelines across all candidates and DSA problems, and displays
executive summary reports with risk scores and flagged candidates.
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path to ensure module imports work smoothly
sys.path.insert(0, str(Path(__file__).parent))

from config import DEFAULT_MODEL, RISK_THRESHOLD
from generate_samples import generate_all_samples
from proctor_engine import OnlineCodingProctorEngine


def print_banner() -> None:
    """Prints a styled ASCII banner for the assessment system."""
    print("=" * 75)
    print("    AUTOMATED CODING MULTIAGENT PROCTORING SYSTEM")
    print("    Powered by Groq API ('openai/gpt-oss-120b') & MOSS Winnowing")
    print("=" * 75)


def run_full_proctoring_round() -> None:
    """
    Executes an entire online coding assessment round across all DSA problems and submissions.
    """
    print_banner()

    engine = OnlineCodingProctorEngine()

    # 1. Generate sample problems and candidate submissions
    generate_all_samples(engine)

    all_problem_ids = list(engine.problems.keys())
    total_evaluations = 0
    flagged_candidates_count = 0

    summary_matrix = []

    print("\n" + "=" * 75)
    print("    PROCESSING ONLINE CODING ROUND EVALUATIONS")
    print("=" * 75)

    for problem_id in all_problem_ids:
        problem = engine.problems[problem_id]
        print(f"\n>>> EVALUATING DSA PROBLEM: [{problem.problem_id}] - '{problem.title}'")
        print("-" * 75)

        submissions = engine.get_all_submissions_for_problem(problem_id)
        for sub in submissions:
            cand_id = sub.candidate_id
            print(f"\n [*] Analyzing Candidate Submission: '{cand_id}'...")

            # Run full proctoring pipeline
            risk_result = engine.evaluate_submission(cand_id, problem_id)
            total_evaluations += 1

            # Format terminal outputs
            status_symbol = "⚠️  [FLAGGED]" if risk_result.is_flagged else "✅ [CLEAR]"
            if risk_result.is_flagged:
                flagged_candidates_count += 1

            print(f"     Status: {status_symbol} {risk_result.recommendation}")
            print(f"     Weighted Risk Score: {risk_result.overall_risk:.1%} (Threshold: {RISK_THRESHOLD:.0%})")
            print(f"     - MOSS Code Similarity Score : {risk_result.code_similarity_score:.1%} (Nearest match: '{risk_result.most_similar_candidate}')")
            print(f"     - Same Bug Analysis Score    : {risk_result.same_bug_score:.1%} (Collusion partner: '{risk_result.collusion_partner}')")
            print(f"     - AI Forensics Probability   : {risk_result.ai_probability:.1%}")

            print("     - Evidence & Findings:")
            for reason in risk_result.reasons:
                print(f"        • {reason}")

            summary_matrix.append({
                "problem": problem.problem_id,
                "candidate": cand_id,
                "risk_score": risk_result.overall_risk,
                "is_flagged": risk_result.is_flagged,
                "recommendation": risk_result.recommendation,
                "similarity_score": risk_result.code_similarity_score,
                "most_similar": risk_result.most_similar_candidate,
                "same_bug_score": risk_result.same_bug_score,
                "collusion_partner": risk_result.collusion_partner,
                "ai_probability": risk_result.ai_probability
            })

    # Display Executive Summary Table
    print("\n" + "=" * 85)
    print("                 EXECUTIVE PROCTORING AUDIT SUMMARY")
    print("=" * 85)
    print(f"{'PROBLEM':<25} | {'CANDIDATE':<20} | {'RISK %':<8} | {'STATUS':<20}")
    print("-" * 85)

    for item in summary_matrix:
        risk_str = f"{item['risk_score']:.1%}"
        flag_str = "⚠️ FLAGGED (>70%)" if item['is_flagged'] else "CLEAR"
        print(f"{item['problem']:<25} | {item['candidate']:<20} | {risk_str:<8} | {flag_str:<20}")

    print("=" * 85)
    print(f" Total Submissions Analyzed : {total_evaluations}")
    print(f" Candidates Flagged (>70%)  : {flagged_candidates_count}")
    print(" Reports Saved To           : ./data/reports/")
    print("=" * 85 + "\n")


if __name__ == "__main__":
    run_full_proctoring_round()
