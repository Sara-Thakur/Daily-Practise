"""
AI Coding Proctoring System
===========================

Features:
    1. MOSS-like structural code similarity
    2. Variable-name normalization
    3. Hidden-test failure-pattern comparison
    4. Groq-based AI baseline generation
    5. Groq-based AI-characteristics judge
    6. Weighted risk scoring

Installation:
    pip install groq python-dotenv

Environment:
    Create a .env file:

        GROQ_API_KEY=your_api_key_here

Run:
    python proctor.py

IMPORTANT:
    The sandbox executor below is intentionally a safe placeholder.
    NEVER execute untrusted student code directly with exec() on your
    production backend. Use an isolated Docker/VM/Firecracker sandbox.
"""

from __future__ import annotations

import ast
import hashlib
import io
import json
import os
import tokenize
from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional, Sequence, Set, Tuple

from dotenv import load_dotenv
from groq import Groq


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

DEFAULT_MODEL = "openai/gpt-oss-120b"

SIMILARITY_WEIGHT = 0.40
BUG_WEIGHT = 0.40
AI_WEIGHT = 0.20


# ============================================================
# DATA MODELS
# ============================================================

@dataclass
class Submission:
    """Represent a student's programming submission."""

    student_id: str
    source: str


@dataclass
class TestCase:
    """Represent a hidden test case."""

    test_id: str
    input_data: Any
    expected_output: Any


@dataclass
class BugPattern:
    """Represent the result of running a submission against hidden tests."""

    student_id: str
    failures: List[bool]
    error_types: List[Optional[str]]
    outputs: List[Optional[str]] = field(default_factory=list)


@dataclass
class AIDetectionResult:
    """Represent the Groq judge's AI-characteristics assessment."""

    probability: float
    confidence: float
    reasons: List[str]
    baseline_matches: List[str] = field(default_factory=list)


@dataclass
class RiskResult:
    """Represent the final aggregate risk assessment."""

    probability: float
    components: dict
    evidence: dict


# ============================================================
# GROQ CLIENT
# ============================================================

class GroqClient:
    """Wrapper around the Groq API."""

    def __init__(self, model: str = DEFAULT_MODEL):
        """
        Initialize the Groq client.

        Args:
            model: Groq model to use.

        Raises:
            RuntimeError: If GROQ_API_KEY is missing.
        """
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is missing.\n"
                "Create a .env file containing:\n\n"
                "GROQ_API_KEY=your_api_key_here"
            )

        self.client = Groq(api_key=api_key)
        self.model = model

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
    ) -> str:
        """
        Send a chat-completion request to Groq.

        Args:
            system_prompt: System instructions.
            user_prompt: User/task prompt.
            temperature: Sampling temperature.

        Returns:
            Generated model response.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            temperature=temperature,
        )

        return response.choices[0].message.content or ""


# ============================================================
# CODE NORMALIZATION
# ============================================================

PYTHON_KEYWORDS = {
    "and",
    "as",
    "assert",
    "async",
    "await",
    "break",
    "case",
    "class",
    "continue",
    "def",
    "del",
    "elif",
    "else",
    "except",
    "False",
    "finally",
    "for",
    "from",
    "global",
    "if",
    "import",
    "in",
    "is",
    "lambda",
    "match",
    "None",
    "nonlocal",
    "not",
    "or",
    "pass",
    "raise",
    "return",
    "True",
    "try",
    "type",
    "while",
    "with",
    "yield",
}


def normalize_python_code(source: str) -> List[str]:
    """
    Tokenize Python code while normalizing identifiers.

    Variable/function/class names are replaced with IDENT.
    Numbers become NUMBER and strings become STRING.

    Args:
        source: Python source code.

    Returns:
        Normalized token list.

    Raises:
        SyntaxError: If the code is syntactically invalid.
    """
    ast.parse(source)

    tokens = []

    stream = io.StringIO(source).readline

    for token in tokenize.generate_tokens(stream):
        token_type = token.type
        token_string = token.string

        if token_type in {
            tokenize.ENCODING,
            tokenize.NL,
            tokenize.NEWLINE,
            tokenize.INDENT,
            tokenize.DEDENT,
            tokenize.COMMENT,
        }:
            continue

        if token_type == tokenize.NAME:

            if token_string in PYTHON_KEYWORDS:
                tokens.append(f"KW:{token_string}")
            else:
                tokens.append("IDENT")

        elif token_type == tokenize.NUMBER:
            tokens.append("NUMBER")

        elif token_type == tokenize.STRING:
            tokens.append("STRING")

        else:
            tokens.append(f"{token_type}:{token_string}")

    return tokens


# ============================================================
# MOSS-LIKE FINGERPRINTING
# ============================================================

def hash_ngram(tokens: List[str]) -> int:
    """
    Hash a token n-gram using BLAKE2b.

    Args:
        tokens: Token sequence.

    Returns:
        Integer hash value.
    """
    data = "\x1f".join(tokens).encode("utf-8")

    digest = hashlib.blake2b(
        data,
        digest_size=8,
    ).digest()

    return int.from_bytes(digest, "big")


def generate_fingerprints(
    tokens: List[str],
    k: int = 7,
    window: int = 4,
) -> Set[int]:
    """
    Generate MOSS-like fingerprints using k-grams and winnowing.

    Args:
        tokens: Normalized token sequence.
        k: Number of tokens in each gram.
        window: Winnowing window size.

    Returns:
        Set of fingerprints.
    """
    if k <= 0 or window <= 0:
        raise ValueError("k and window must be positive")

    if len(tokens) < k:
        return set()

    hashes = [
        hash_ngram(tokens[i:i + k])
        for i in range(len(tokens) - k + 1)
    ]

    if len(hashes) <= window:
        return {min(hashes)}

    fingerprints = set()

    for i in range(len(hashes) - window + 1):
        current_window = hashes[i:i + window]

        fingerprints.add(min(current_window))

    return fingerprints


def fingerprint_code(
    source: str,
    k: int = 7,
    window: int = 4,
) -> Set[int]:
    """
    Convert Python source code into structural fingerprints.

    Args:
        source: Python source code.
        k: Token n-gram size.
        window: Winnowing window.

    Returns:
        Fingerprint set.
    """
    tokens = normalize_python_code(source)

    return generate_fingerprints(
        tokens,
        k=k,
        window=window,
    )


def jaccard_similarity(
    fingerprints_a: Set[int],
    fingerprints_b: Set[int],
) -> float:
    """
    Calculate Jaccard similarity.

    Args:
        fingerprints_a: First fingerprint set.
        fingerprints_b: Second fingerprint set.

    Returns:
        Similarity between 0 and 1.
    """
    if not fingerprints_a and not fingerprints_b:
        return 1.0

    union = fingerprints_a | fingerprints_b

    if not union:
        return 0.0

    intersection = fingerprints_a & fingerprints_b

    return len(intersection) / len(union)


def compare_code(
    source_a: str,
    source_b: str,
) -> float:
    """
    Compare two Python programs structurally.

    Args:
        source_a: First program.
        source_b: Second program.

    Returns:
        Structural similarity from 0 to 1.
    """
    fp_a = fingerprint_code(source_a)
    fp_b = fingerprint_code(source_b)

    return jaccard_similarity(fp_a, fp_b)


# ============================================================
# HIDDEN TEST / BUG DETECTION
# ============================================================

def classify_exception(exc: BaseException) -> str:
    """
    Convert an exception into a stable error category.

    Args:
        exc: Exception raised by student code.

    Returns:
        Exception class name.
    """
    return type(exc).__name__


def run_hidden_tests(
    submission: str,
    student_id: str,
    test_cases: Sequence[TestCase],
    executor: Callable[[str, Any], Any],
) -> BugPattern:
    """
    Run a submission against hidden test cases.

    Args:
        submission: Student source code.
        student_id: Student identifier.
        test_cases: Hidden tests.
        executor: Secure sandbox execution function.

    Returns:
        BugPattern describing failures.
    """
    failures = []
    error_types = []
    outputs = []

    for test in test_cases:

        try:
            actual = executor(
                submission,
                test.input_data,
            )

            passed = actual == test.expected_output

            failures.append(not passed)

            if passed:
                error_types.append(None)
            else:
                error_types.append("WRONG_ANSWER")

            outputs.append(repr(actual))

        except BaseException as exc:

            failures.append(True)
            error_types.append(
                classify_exception(exc)
            )
            outputs.append(None)

    return BugPattern(
        student_id=student_id,
        failures=failures,
        error_types=error_types,
        outputs=outputs,
    )


def failure_signature(
    pattern: BugPattern,
) -> Tuple:
    """
    Convert a bug pattern into a comparison signature.

    Args:
        pattern: Bug pattern.

    Returns:
        Hashable tuple.
    """
    return tuple(
        zip(
            pattern.failures,
            pattern.error_types,
        )
    )


def compare_bug_patterns(
    pattern_a: BugPattern,
    pattern_b: BugPattern,
) -> float:
    """
    Compare two hidden-test failure patterns.

    Args:
        pattern_a: First pattern.
        pattern_b: Second pattern.

    Returns:
        Similarity from 0 to 1.
    """
    if len(pattern_a.failures) != len(
        pattern_b.failures
    ):
        raise ValueError(
            "Both submissions must use the same tests."
        )

    if not pattern_a.failures:
        return 0.0

    signature_a = failure_signature(pattern_a)
    signature_b = failure_signature(pattern_b)

    matches = sum(
        a == b
        for a, b in zip(
            signature_a,
            signature_b,
        )
    )

    return matches / len(signature_a)


# ============================================================
# GROQ BASELINE GENERATION
# ============================================================

def generate_baselines(
    assignment: str,
    groq: GroqClient,
    count: int = 3,
) -> List[str]:
    """
    Generate independent AI solutions for an assignment.

    Args:
        assignment: Coding problem.
        groq: Groq client.
        count: Number of baseline solutions.

    Returns:
        List of generated solutions.
    """
    baselines = []

    prompt = f"""
Solve this programming problem.

Return ONLY the Python source code.
Do not use Markdown.
Do not explain your answer.

Problem:

{assignment}
"""

    for _ in range(count):

        solution = groq.complete(
            system_prompt=(
                "You are an expert Python programmer."
            ),
            user_prompt=prompt,
            temperature=0.7,
        )

        # Remove accidental Markdown fences.
        solution = solution.strip()

        if solution.startswith("```"):
            lines = solution.splitlines()

            if lines:
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            solution = "\n".join(lines)

        baselines.append(solution)

    return baselines


# ============================================================
# GROQ AI JUDGE
# ============================================================

def build_judge_prompt(
    assignment: str,
    submission: str,
    baselines: Sequence[str],
) -> str:
    """
    Build the prompt used by the Groq judge.

    Args:
        assignment: Original assignment.
        submission: Student code.
        baselines: AI-generated reference solutions.

    Returns:
        Judge prompt.
    """
    baseline_text = ""

    for index, baseline in enumerate(baselines, 1):

        baseline_text += (
            f"\n\n===== BASELINE {index} =====\n"
            f"{baseline}"
        )

    return f"""
You are assisting with academic-integrity review.

IMPORTANT:
You are NOT determining whether the student cheated.

Assess only observable characteristics of the submitted code.

Assignment:
{assignment}

Student submission:
===== STUDENT CODE =====

{submission}

AI-generated reference solutions:
{baseline_text}

Analyze:

1. Structural resemblance to the generated baselines.
2. Unusually generic implementation patterns.
3. Stylistic consistency.
4. Comments and documentation style.
5. Internal stylistic discontinuities.
6. Unusual sophistication relative to the assignment.
7. Other observable characteristics.

Do NOT assume that:
- clean code is AI-generated,
- correct code is AI-generated,
- lack of mistakes means AI-generated,
- a student using good formatting used AI.

A human can write polished code.
An AI can generate messy code.

Return ONLY valid JSON:

{{
    "probability": 0.0,
    "confidence": 0.0,
    "reasons": [],
    "baseline_matches": []
}}

probability:
Your uncertain estimate of how strongly the observable characteristics
resemble AI-generated code.

confidence:
How confident you are in that assessment.

Both values must be between 0 and 1.
"""


def judge_ai_characteristics(
    assignment: str,
    submission: str,
    baselines: Sequence[str],
    groq: GroqClient,
) -> AIDetectionResult:
    """
    Ask Groq to evaluate observable AI-like characteristics.

    Args:
        assignment: Coding assignment.
        submission: Student source.
        baselines: AI-generated baselines.
        groq: Groq client.

    Returns:
        AIDetectionResult.
    """
    prompt = build_judge_prompt(
        assignment,
        submission,
        baselines,
    )

    raw = groq.complete(
        system_prompt=(
            "You are a careful academic-integrity "
            "code-review assistant. "
            "Return valid JSON only."
        ),
        user_prompt=prompt,
        temperature=0.0,
    )

    try:
        # Handle accidental Markdown fences.
        cleaned = raw.strip()

        if cleaned.startswith("```"):
            lines = cleaned.splitlines()

            if lines:
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            cleaned = "\n".join(lines)

        data = json.loads(cleaned)

        probability = float(
            data.get("probability", 0)
        )

        confidence = float(
            data.get("confidence", 0)
        )

        probability = max(
            0.0,
            min(1.0, probability),
        )

        confidence = max(
            0.0,
            min(1.0, confidence),
        )

        return AIDetectionResult(
            probability=probability,
            confidence=confidence,
            reasons=list(
                data.get("reasons", [])
            ),
            baseline_matches=list(
                data.get(
                    "baseline_matches",
                    [],
                )
            ),
        )

    except (
        ValueError,
        TypeError,
        json.JSONDecodeError,
    ):

        return AIDetectionResult(
            probability=0.0,
            confidence=0.0,
            reasons=[
                "Groq judge returned invalid JSON."
            ],
        )


# ============================================================
# RISK SCORING
# ============================================================

def calculate_risk(
    similarity_score: float,
    bug_similarity_score: float,
    ai_result: AIDetectionResult,
) -> RiskResult:
    """
    Combine all detection signals into one risk score.

    Args:
        similarity_score: Structural code similarity.
        bug_similarity_score: Hidden-test behavior similarity.
        ai_result: Groq AI-characteristics result.

    Returns:
        RiskResult with score and evidence.
    """
    similarity_score = max(
        0.0,
        min(1.0, similarity_score),
    )

    bug_similarity_score = max(
        0.0,
        min(1.0, bug_similarity_score),
    )

    # Reduce influence of an uncertain AI judgment.
    ai_score = (
        ai_result.probability
        * ai_result.confidence
    )

    total_weight = (
        SIMILARITY_WEIGHT
        + BUG_WEIGHT
        + AI_WEIGHT
    )

    risk = (
        SIMILARITY_WEIGHT * similarity_score
        + BUG_WEIGHT * bug_similarity_score
        + AI_WEIGHT * ai_score
    ) / total_weight

    return RiskResult(
        probability=max(
            0.0,
            min(1.0, risk),
        ),
        components={
            "code_similarity": similarity_score,
            "bug_similarity": bug_similarity_score,
            "ai_characteristics": ai_score,
        },
        evidence={
            "ai_probability": ai_result.probability,
            "ai_confidence": ai_result.confidence,
            "ai_reasons": ai_result.reasons,
            "baseline_matches": (
                ai_result.baseline_matches
            ),
        },
    )


# ============================================================
# SANDBOX PLACEHOLDER
# ============================================================

def sandbox_executor(
    source: str,
    input_data: Any,
) -> Any:
    """
    Execute student code in a secure external sandbox.

    THIS FUNCTION IS ONLY A PLACEHOLDER.

    Never execute untrusted student source directly inside
    your production API process.

    Recommended architecture:

        Backend
           |
           v
        Job Queue
           |
           v
        Docker / VM / Firecracker
           |
           v
        Restricted student process

    The sandbox should enforce:
        - CPU limit
        - memory limit
        - execution timeout
        - process limit
        - restricted filesystem
        - no secrets
        - restricted/no network
        - output-size limit

    Args:
        source: Student source.
        input_data: Test input.

    Returns:
        Program output.

    Raises:
        NotImplementedError: Always, until a real sandbox is connected.
    """
    raise NotImplementedError(
        "Connect sandbox_executor() to a secure "
        "code execution service."
    )


# ============================================================
# COMPLETE ANALYSIS
# ============================================================

def analyze_submission(
    submission: Submission,
    comparison: Submission,
    assignment: str,
    hidden_tests: Sequence[TestCase],
    groq: GroqClient,
    executor: Callable[[str, Any], Any],
) -> RiskResult:
    """
    Run the complete proctoring pipeline.

    Args:
        submission: Student being analyzed.
        comparison: Another submission for comparison.
        assignment: Original programming assignment.
        hidden_tests: Hidden test suite.
        groq: Groq client.
        executor: Secure sandbox executor.

    Returns:
        Complete RiskResult.
    """

    print("\n[1/4] Running code similarity analysis...")

    similarity = compare_code(
        submission.source,
        comparison.source,
    )

    print(
        f"      Similarity: {similarity:.2%}"
    )

    print(
        "\n[2/4] Running hidden-test "
        "behavior analysis..."
    )

    student_pattern = run_hidden_tests(
        submission.source,
        submission.student_id,
        hidden_tests,
        executor,
    )

    comparison_pattern = run_hidden_tests(
        comparison.source,
        comparison.student_id,
        hidden_tests,
        executor,
    )

    bug_similarity = compare_bug_patterns(
        student_pattern,
        comparison_pattern,
    )

    print(
        f"      Bug-pattern similarity: "
        f"{bug_similarity:.2%}"
    )

    print(
        "\n[3/4] Generating AI baselines "
        "with Groq..."
    )

    baselines = generate_baselines(
        assignment,
        groq,
        count=3,
    )

    print(
        f"      Generated {len(baselines)} baselines."
    )

    print(
        "\n      Asking Groq judge..."
    )

    ai_result = judge_ai_characteristics(
        assignment,
        submission.source,
        baselines,
        groq,
    )

    print(
        f"      AI-characteristics probability: "
        f"{ai_result.probability:.2%}"
    )

    print(
        f"      Judge confidence: "
        f"{ai_result.confidence:.2%}"
    )

    print(
        "\n[4/4] Calculating aggregate risk..."
    )

    result = calculate_risk(
        similarity_score=similarity,
        bug_similarity_score=bug_similarity,
        ai_result=ai_result,
    )

    return result


# ============================================================
# DISPLAY RESULT
# ============================================================

def print_result(result: RiskResult) -> None:
    """
    Display the final proctoring result.

    Args:
        result: RiskResult returned by the pipeline.
    """
    print("\n")
    print("=" * 60)
    print("CODING PROCTORING RESULT")
    print("=" * 60)

    print(
        f"\nOverall review risk: "
        f"{result.probability:.2%}"
    )

    print("\nComponents:")

    for name, value in result.components.items():
        print(
            f"  - {name}: {value:.2%}"
        )

    print("\nEvidence:")

    for name, value in result.evidence.items():
        print(
            f"  - {name}: {value}"
        )

    print("\nInterpretation:")

    if result.probability >= 0.75:
        print(
            "  HIGH REVIEW PRIORITY"
        )
    elif result.probability >= 0.50:
        print(
            "  MEDIUM REVIEW PRIORITY"
        )
    else:
        print(
            "  LOW REVIEW PRIORITY"
        )

    print(
        "\nNOTE: This is an automated review signal, "
        "not a determination of cheating."
    )

    print("=" * 60)


# ============================================================
# DEMO
# ============================================================

def main() -> None:
    """
    Run a demonstration of the complete pipeline.
    """

    print("=" * 60)
    print("AI CODING PROCTOR")
    print("=" * 60)

    # --------------------------------------------------------
    # Initialize Groq
    # --------------------------------------------------------

    try:
        groq = GroqClient()

    except RuntimeError as exc:
        print(f"\nERROR: {exc}")
        return

    # --------------------------------------------------------
    # Assignment
    # --------------------------------------------------------

    assignment = """
Write a Python function called solve(numbers) that returns
the sum of all positive even numbers in the list.

Example:

solve([1, 2, 3, 4]) -> 6
solve([-2, 2, 5]) -> 2
solve([]) -> 0
"""

    # --------------------------------------------------------
    # Student submission
    # --------------------------------------------------------

    student = Submission(
        student_id="student-001",
        source="""
def solve(numbers):
    total = 0

    for number in numbers:
        if number > 0 and number % 2 == 0:
            total += number

    return total
""",
    )

    # --------------------------------------------------------
    # Comparison submission
    # --------------------------------------------------------

    comparison = Submission(
        student_id="student-002",
        source="""
def solve(values):
    result = 0

    for value in values:
        if value > 0 and value % 2 == 0:
            result += value

    return result
""",
    )

    # --------------------------------------------------------
    # Hidden tests
    # --------------------------------------------------------

    hidden_tests = [
        TestCase(
            test_id="test-001",
            input_data=[1, 2, 3, 4],
            expected_output=6,
        ),
        TestCase(
            test_id="test-002",
            input_data=[-2, -4, 2],
            expected_output=2,
        ),
        TestCase(
            test_id="test-003",
            input_data=[],
            expected_output=0,
        ),
        TestCase(
            test_id="test-004",
            input_data=[1, 3, 5, 7],
            expected_output=0,
        ),
    ]

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # The placeholder sandbox will intentionally raise an
    # exception. For the first test of the system, you can
    # temporarily skip hidden-test analysis or connect a real
    # sandbox here.
    # --------------------------------------------------------

    try:

        result = analyze_submission(
            submission=student,
            comparison=comparison,
            assignment=assignment,
            hidden_tests=hidden_tests,
            groq=groq,
            executor=sandbox_executor,
        )

        print_result(result)

    except NotImplementedError:

        print("\n")
        print("=" * 60)
        print("SANDBOX NOT CONFIGURED")
        print("=" * 60)
        print(
            "\nGroq and similarity components are ready,"
            " but hidden-test execution requires a secure"
            " sandbox."
        )
        print(
            "\nDo NOT replace the sandbox with exec() "
            "in production."
        )

    except Exception as exc:

        print("\nPipeline error:")
        print(type(exc).__name__, str(exc))


if __name__ == "__main__":
    main()
