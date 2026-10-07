"""Detection of correlated failure patterns across submissions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

from .models import BugPattern


@dataclass
class TestCase:
    """Represent a hidden test case."""

    test_id: str
    input_data: object
    expected_output: object


@dataclass
class TestObservation:
    """Represent the result of running one submission against one test."""

    passed: bool
    error_type: Optional[str]
    output: Optional[str]


def classify_exception(exc: BaseException) -> str:
    """
    Convert an exception into a stable error category.

    Args:
        exc: Exception raised during execution.

    Returns:
        A normalized exception type name.
    """
    return type(exc).__name__


def run_hidden_tests(
    submission: str,
    test_cases: Sequence[TestCase],
    executor: Callable[[str, object], object],
) -> BugPattern:
    """
    Execute a submission against hidden tests and build its failure signature.

    The executor is deliberately injected rather than implemented here.
    In production it should execute code inside a sandbox with CPU, memory,
    filesystem, network, and execution-time restrictions.

    Args:
        submission: Student source code.
        test_cases: Hidden tests.
        executor: Sandboxed execution function.

    Returns:
        A BugPattern describing the observed behavior.
    """
    failures: List[bool] = []
    error_types: List[Optional[str]] = []
    outputs: List[Optional[str]] = []

    for test in test_cases:
        try:
            actual = executor(submission, test.input_data)

            passed = actual == test.expected_output

            failures.append(not passed)
            error_types.append(None if passed else "WRONG_ANSWER")
            outputs.append(repr(actual))

        except BaseException as exc:
            failures.append(True)
            error_types.append(classify_exception(exc))
            outputs.append(None)

    return BugPattern(
        student_id="unknown",
        failures=failures,
        error_types=error_types,
        outputs=outputs,
    )


def failure_signature(pattern: BugPattern) -> Tuple:
    """
    Convert a bug pattern into a hashable comparison signature.

    Args:
        pattern: Observed bug pattern.

    Returns:
        Tuple suitable for equality/grouping.
    """
    return tuple(
        (failed, error_type)
        for failed, error_type in zip(
            pattern.failures,
            pattern.error_types,
        )
    )


def compare_bug_patterns(
    pattern_a: BugPattern,
    pattern_b: BugPattern,
) -> float:
    """
    Calculate similarity between two hidden-test failure patterns.

    Args:
        pattern_a: First student's pattern.
        pattern_b: Second student's pattern.

    Returns:
        Similarity in [0, 1].
    """
    if len(pattern_a.failures) != len(pattern_b.failures):
        raise ValueError("Test suites must contain the same number of cases")

    if not pattern_a.failures:
        return 0.0

    matches = sum(
        a == b
        for a, b in zip(
            failure_signature(pattern_a),
            failure_signature(pattern_b),
        )
    )

    return matches / len(pattern_a.failures)


def find_matching_bug_groups(
    patterns: Sequence[BugPattern],
    threshold: float = 0.9,
) -> List[List[str]]:
    """
    Group submissions exhibiting highly similar hidden-test behavior.

    Args:
        patterns: Failure patterns for multiple students.
        threshold: Minimum behavioral similarity for grouping.

    Returns:
        Groups of student IDs with similar failure patterns.
    """
    groups: List[List[str]] = []
    assigned = set()

    for i, pattern_a in enumerate(patterns):
        if pattern_a.student_id in assigned:
            continue

        group = [pattern_a.student_id]

        for pattern_b in patterns[i + 1:]:
            similarity = compare_bug_patterns(pattern_a, pattern_b)

            if similarity >= threshold:
                group.append(pattern_b.student_id)

        if len(group) > 1:
            groups.append(group)
            assigned.update(group)

    return groups
