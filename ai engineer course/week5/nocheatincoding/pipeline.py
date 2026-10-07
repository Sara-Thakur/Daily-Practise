"""End-to-end coding-integrity analysis pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Sequence

from .ai_detection import (
    generate_baselines,
    judge_ai_characteristics,
)
from .bug_detection import (
    TestCase,
    compare_bug_patterns,
    run_hidden_tests,
)
from .models import BugPattern, RiskResult
from .risk import combine_risk
from .similarity import compare_code


@dataclass
class Submission:
    """Represent a student's programming submission."""

    student_id: str
    source: str


def analyze_submission(
    submission: Submission,
    assignment: str,
    comparison_submission: Submission,
    hidden_tests: Sequence[TestCase],
    executor: Callable,
    baseline_llm: Callable[[str], str],
    judge_llm: Callable[[str], str],
) -> RiskResult:
    """
    Run all detection modules against a single submission.

    Args:
        submission: Student submission being evaluated.
        assignment: Original coding prompt.
        comparison_submission: Submission used for similarity analysis.
        hidden_tests: Hidden behavioral test cases.
        executor: Secure sandbox execution function.
        baseline_llm: LLM used to generate reference solutions.
        judge_llm: LLM used to assess AI-like characteristics.

    Returns:
        Aggregate review-risk result.
    """
    # 1. Structural similarity.
    similarity = compare_code(
        submission.source,
        comparison_submission.source,
    )

    # 2. Hidden-test behavior.
    student_bug_pattern = run_hidden_tests(
        submission.source,
        hidden_tests,
        executor,
    )
    student_bug_pattern.student_id = submission.student_id

    comparison_bug_pattern = run_hidden_tests(
        comparison_submission.source,
        hidden_tests,
        executor,
    )
    comparison_bug_pattern.student_id = (
        comparison_submission.student_id
    )

    bug_similarity = compare_bug_patterns(
        student_bug_pattern,
        comparison_bug_pattern,
    )

    # 3. AI-characteristics analysis.
    baselines = generate_baselines(
        assignment,
        baseline_llm,
    )

    ai_result = judge_ai_characteristics(
        assignment,
        submission.source,
        baselines,
        judge_llm,
    )

    # 4. Aggregate.
    return combine_risk(
        similarity_score=similarity,
        bug_similarity_score=bug_similarity,
        ai_result=ai_result,
    )
