"""Structural code similarity analysis."""

from __future__ import annotations

import ast
import hashlib
import io
import tokenize
from typing import Dict, Iterable, List, Set, Tuple


IGNORED_TOKEN_TYPES = {
    tokenize.ENCODING,
    tokenize.NL,
    tokenize.NEWLINE,
    tokenize.INDENT,
    tokenize.DEDENT,
    tokenize.COMMENT,
}


def normalize_python_code(source: str) -> List[str]:
    """
    Tokenize Python source while normalizing identifiers.

    Variable, function, class, and argument names are replaced with
    generic placeholders. Python keywords and literals remain distinguishable.

    Args:
        source: Python source code.

    Returns:
        A normalized token sequence.

    Raises:
        SyntaxError: If the source cannot be tokenized as valid Python.
    """
    tokens: List[str] = []

    # This also gives us a useful syntax check.
    ast.parse(source)

    stream = io.StringIO(source).readline

    for token in tokenize.generate_tokens(stream):
        token_type = token.type
        token_string = token.string

        if token_type in IGNORED_TOKEN_TYPES:
            continue

        if token_type == tokenize.NAME:
            if token_string in {
                "and", "as", "assert", "async", "await", "break",
                "case", "class", "continue", "def", "del", "elif",
                "else", "except", "False", "finally", "for", "from",
                "global", "if", "import", "in", "is", "lambda",
                "match", "None", "nonlocal", "not", "or", "pass",
                "raise", "return", "True", "try", "type", "while",
                "with", "yield",
            }:
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


def hash_ngram(tokens: List[str]) -> int:
    """
    Hash a token n-gram into a stable integer.

    Args:
        tokens: Token sequence forming one n-gram.

    Returns:
        A 64-bit integer hash.
    """
    data = "\x1f".join(tokens).encode("utf-8")
    digest = hashlib.blake2b(data, digest_size=8).digest()
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
        A set of selected fingerprint hashes.
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

    fingerprints: Set[int] = set()

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
    Convert source code into a set of structural fingerprints.

    Args:
        source: Source code.
        k: Token n-gram size.
        window: Winnowing window size.

    Returns:
        A set of structural fingerprints.
    """
    tokens = normalize_python_code(source)
    return generate_fingerprints(tokens, k=k, window=window)


def jaccard_similarity(
    fingerprints_a: Set[int],
    fingerprints_b: Set[int],
) -> float:
    """
    Calculate Jaccard similarity between two fingerprint sets.

    Args:
        fingerprints_a: First fingerprint set.
        fingerprints_b: Second fingerprint set.

    Returns:
        Similarity in the range [0, 1].
    """
    if not fingerprints_a and not fingerprints_b:
        return 1.0

    union = fingerprints_a | fingerprints_b

    if not union:
        return 0.0

    return len(fingerprints_a & fingerprints_b) / len(union)


def compare_code(
    source_a: str,
    source_b: str,
    k: int = 7,
    window: int = 4,
) -> float:
    """
    Compare two source files for structural similarity.

    Variable names are normalized before comparison.

    Args:
        source_a: First source file.
        source_b: Second source file.
        k: Token n-gram size.
        window: Winnowing window size.

    Returns:
        Structural similarity in [0, 1].
    """
    fp_a = fingerprint_code(source_a, k=k, window=window)
    fp_b = fingerprint_code(source_b, k=k, window=window)

    return jaccard_similarity(fp_a, fp_b)
