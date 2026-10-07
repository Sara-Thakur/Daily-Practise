"""
Same Bug Analysis Module for Detecting Identical Hidden Test Case Failure Patterns.

Executes student submissions against hidden test cases in a controlled namespace,
extracts failure signatures (error types, failing test IDs, actual outputs), and
compares failure patterns across candidate submissions to flag potential collusion.
"""

from __future__ import annotations

import sys
import traceback
from typing import Any, Dict, List, Optional, Tuple

from models import BugPattern, SameBugResult, TestCase, TestResult


def execute_submission_on_test(
    source_code: str,
    entrypoint: str,
    test_case: TestCase
) -> TestResult:
    """
    Executes a student submission against a single test case safely.

    Args:
        source_code: Python source code of the candidate submission.
        entrypoint: Target function name to execute.
        test_case: TestCase object containing input_data and expected_output.

    Returns:
        TestResult indicating pass/fail, error classification, and actual output string.
    """
    local_scope: Dict[str, Any] = {}

    try:
        # Compile source code to detect syntax errors prior to execution
        compiled_code = compile(source_code, filename="<candidate_submission>", mode="exec")

        # Execute code in clean local namespace
        exec(compiled_code, local_scope)

        if entrypoint not in local_scope:
            return TestResult(
                test_id=test_case.test_id,
                passed=False,
                error_type="MISSING_ENTRYPOINT",
                error_message=f"Function '{entrypoint}' not defined in submission."
            )

        func = local_scope[entrypoint]

        # Handle positional tuple vs single argument inputs
        if isinstance(test_case.input_data, tuple):
            actual_output = func(*test_case.input_data)
        else:
            actual_output = func(test_case.input_data)

        # Check if actual output matches expected output
        passed = (actual_output == test_case.expected_output)

        return TestResult(
            test_id=test_case.test_id,
            passed=passed,
            actual_output=str(actual_output),
            error_type="PASSED" if passed else "WRONG_ANSWER",
            error_message=None if passed else f"Expected {test_case.expected_output}, got {actual_output}"
        )

    except Exception as exc:
        exc_type = type(exc).__name__
        tb_lines = traceback.format_exception_only(type(exc), exc)
        err_msg = tb_lines[-1].strip() if tb_lines else str(exc)

        return TestResult(
            test_id=test_case.test_id,
            passed=False,
            actual_output=None,
            error_type=exc_type,
            error_message=err_msg
        )


def extract_bug_pattern(
    candidate_id: str,
    problem_id: str,
    source_code: str,
    entrypoint: str,
    hidden_tests: List[TestCase]
) -> BugPattern:
    """
    Executes a candidate's code against all hidden test cases to generate a BugPattern signature.

    Args:
        candidate_id: Candidate identifier.
        problem_id: Problem identifier.
        source_code: Python source code.
        entrypoint: Function entrypoint name.
        hidden_tests: List of hidden TestCase objects.

    Returns:
        BugPattern containing individual TestResult outputs and failure signatures.
    """
    results: List[TestResult] = []

    for test in hidden_tests:
        result = execute_submission_on_test(source_code, entrypoint, test)
        results.append(result)

    return BugPattern(
        candidate_id=candidate_id,
        problem_id=problem_id,
        results=results
    )


def compare_bug_patterns(
    pattern1: BugPattern,
    pattern2: BugPattern
) -> SameBugResult:
    """
    Compares two candidate failure patterns across hidden test cases.

    If two candidates fail on identical test cases with identical error classifications
    (e.g., both raise IndexError on hidden test case #3), this provides strong empirical
    evidence of collusion or copied code logic.

    Args:
        pattern1: BugPattern for candidate 1.
        pattern2: BugPattern for candidate 2.

    Returns:
        SameBugResult object detailing failure pattern similarity and collusion flag.
    """
    results1 = {r.test_id: r for r in pattern1.results}
    results2 = {r.test_id: r for r in pattern2.results}

    all_test_ids = set(results1.keys()) | set(results2.keys())
    if not all_test_ids:
        return SameBugResult(
            candidate_1=pattern1.candidate_id,
            candidate_2=pattern2.candidate_id,
            problem_id=pattern1.problem_id,
            same_bug_score=0.0,
            shared_failed_tests=[],
            is_collusion_suspect=False
        )

    shared_failed_tests: List[str] = []
    identical_failure_matches = 0
    total_failures = 0

    for tid in sorted(all_test_ids):
        res1 = results1.get(tid)
        res2 = results2.get(tid)

        if not res1 or not res2:
            continue

        # Evaluate failed test cases
        if not res1.passed or not res2.passed:
            total_failures += 1

            # Check if both candidates failed on this test case with the same error type
            if not res1.passed and not res2.passed:
                if res1.error_type == res2.error_type:
                    identical_failure_matches += 1
                    shared_failed_tests.append(f"{tid}:{res1.error_type}")

    if total_failures == 0:
        # Both candidates passed all tests cleanly
        score = 0.0
        is_suspect = False
    else:
        score = identical_failure_matches / total_failures
        # Flag collusion suspect if 2 or more hidden tests failed identically
        is_suspect = (identical_failure_matches >= 2) or (score == 1.0 and total_failures > 0)

    return SameBugResult(
        candidate_1=pattern1.candidate_id,
        candidate_2=pattern2.candidate_id,
        problem_id=pattern1.problem_id,
        same_bug_score=round(score, 4),
        shared_failed_tests=shared_failed_tests,
        is_collusion_suspect=is_suspect
    )
