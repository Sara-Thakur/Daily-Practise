"""
Code Similarity Analysis Module implementing the MOSS (Measure of Software Similarity) approach.

Tokenizes Python source code, normalizes identifiers to generic variable placeholders (VAR_1, VAR_2, etc.),
strips structural noise/comments/dead code variations, and applies the Winnowing algorithm to generate
k-gram fingerprint sets for accurate structural plagiarism and collusion detection.
"""

from __future__ import annotations

import ast
import hashlib
import io
import tokenize
from typing import Dict, List, Set, Tuple

from config import MOSS_KGRAM_SIZE, MOSS_WINDOW_SIZE
from models import SimilarityResult

# Standard Python language keywords to preserve during identifier normalization
PYTHON_KEYWORDS = {
    "and", "as", "assert", "async", "await", "break", "case", "class",
    "continue", "def", "del", "elif", "else", "except", "False", "finally",
    "for", "from", "global", "if", "import", "in", "is", "lambda", "match",
    "None", "nonlocal", "not", "or", "pass", "raise", "return", "True",
    "try", "type", "while", "with", "yield", "range", "len", "print", "list",
    "dict", "set", "int", "str", "float", "bool", "enumerate", "zip", "sum",
    "min", "max", "abs", "sorted", "append", "extend", "pop"
}


def normalize_code_ast(source_code: str) -> str:
    """
    Strips dead code statements, docstrings, and comments using AST transformations.

    Args:
        source_code: Raw Python source string.

    Returns:
        Cleaned Python source string stripped of unexecuted docstrings and comments.
    """
    try:
        tree = ast.parse(source_code)

        # Remove top-level or function-level docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                if (node.body and isinstance(node.body[0], ast.Expr) and
                        isinstance(node.body[0].value, ast.Constant) and
                        isinstance(node.body[0].value.value, str)):
                    node.body.pop(0)

        return ast.unparse(tree)
    except Exception:
        # Fallback to original source if AST parsing fails due to syntax error
        return source_code


def tokenize_and_normalize(source_code: str) -> Tuple[List[str], Dict[str, str]]:
    """
    Tokenizes Python code while replacing user-defined variable and function names with standard IDs.

    Converts variable names to 'VAR_1', 'VAR_2', etc., mapping identical identifiers consistently
    throughout the snippet. Keeps keywords, operators, numbers, and literals distinguishable.

    Args:
        source_code: Python source code string.

    Returns:
        A tuple containing:
        - List of normalized string tokens.
        - Dictionary mapping original variable names to replaced placeholder IDs.
    """
    cleaned_code = normalize_code_ast(source_code)
    tokens: List[str] = []
    var_map: Dict[str, str] = {}
    var_counter = 1

    stream = io.StringIO(cleaned_code).readline

    try:
        token_gen = tokenize.generate_tokens(stream)
        for tok in token_gen:
            tok_type = tok.type
            tok_str = tok.string.strip()

            # Ignore structural whitespace, line breaks, and comments
            if tok_type in {
                tokenize.ENCODING,
                tokenize.NL,
                tokenize.NEWLINE,
                tokenize.INDENT,
                tokenize.DEDENT,
                tokenize.COMMENT,
            } or not tok_str:
                continue

            if tok_type == tokenize.NAME:
                if tok_str in PYTHON_KEYWORDS:
                    tokens.append(f"KW:{tok_str}")
                else:
                    if tok_str not in var_map:
                        var_map[tok_str] = f"VAR_{var_counter}"
                        var_counter += 1
                    tokens.append(f"ID:{var_map[tok_str]}")

            elif tok_type == tokenize.NUMBER:
                tokens.append("NUM")

            elif tok_type == tokenize.STRING:
                tokens.append("STR")

            elif tok_type == tokenize.OP:
                tokens.append(f"OP:{tok_str}")

            else:
                tokens.append(f"TOK:{tok_str}")
    except Exception:
        # Fallback character-level tokenization if token generator errors
        for word in cleaned_code.split():
            tokens.append(f"RAW:{word}")

    return tokens, var_map


def hash_ngram(ngram: List[str]) -> int:
    """
    Computes a stable 64-bit integer hash for a sequence of normalized tokens using BLAKE2b.

    Args:
        ngram: List of token strings forming a single k-gram.

    Returns:
        64-bit integer hash value.
    """
    payload = "::".join(ngram).encode("utf-8")
    digest = hashlib.blake2b(payload, digest_size=8).digest()
    return int.from_bytes(digest, "big")


def winnow_fingerprints(
    tokens: List[str],
    k: int = MOSS_KGRAM_SIZE,
    w: int = MOSS_WINDOW_SIZE
) -> Set[int]:
    """
    Applies the MOSS Winnowing algorithm to select robust fingerprint hashes.

    Forms k-grams of tokens, hashes each k-gram, and selects the minimum hash value
    in every sliding window of size w.

    Args:
        tokens: Normalized token list.
        k: Size of token n-grams (default from config).
        w: Size of winnowing window (default from config).

    Returns:
        Set of selected integer fingerprint hashes.
    """
    if len(tokens) < k:
        return set()

    # Generate hashes for all contiguous k-grams
    hashes = [
        hash_ngram(tokens[i: i + k])
        for i in range(len(tokens) - k + 1)
    ]

    if not hashes:
        return set()

    if len(hashes) <= w:
        return {min(hashes)}

    fingerprints: Set[int] = set()

    # Sliding window winnowing selection
    for i in range(len(hashes) - w + 1):
        window = hashes[i: i + w]
        min_hash = min(window)
        fingerprints.add(min_hash)

    return fingerprints


def calculate_jaccard_similarity(set_a: Set[int], set_b: Set[int]) -> float:
    """
    Calculates Jaccard similarity index between two fingerprint sets.

    Args:
        set_a: First fingerprint set.
        set_b: Second fingerprint set.

    Returns:
        Float score between 0.0 (completely distinct) and 1.0 (identical structure).
    """
    if not set_a and not set_b:
        return 1.0
    union = set_a | set_b
    if not union:
        return 0.0
    intersection = set_a & set_b
    return len(intersection) / len(union)


def compare_code_similarity(
    candidate_1_id: str,
    code1: str,
    candidate_2_id: str,
    code2: str,
    problem_id: str,
    k: int = MOSS_KGRAM_SIZE,
    w: int = MOSS_WINDOW_SIZE
) -> SimilarityResult:
    """
    Compares two code snippets for structural similarity using normalized MOSS winnowing.

    Detects renamed variables, dead code insertions, and minor re-orderings.

    Args:
        candidate_1_id: Identifier for candidate 1.
        code1: Source code for candidate 1.
        candidate_2_id: Identifier for candidate 2.
        code2: Source code for candidate 2.
        problem_id: ID of the problem being evaluated.
        k: Token k-gram size.
        w: Winnowing window size.

    Returns:
        SimilarityResult object with similarity score and detected obfuscation techniques.
    """
    tokens1, vars1 = tokenize_and_normalize(code1)
    tokens2, vars2 = tokenize_and_normalize(code2)

    fps1 = winnow_fingerprints(tokens1, k=k, w=w)
    fps2 = winnow_fingerprints(tokens2, k=k, w=w)

    similarity = calculate_jaccard_similarity(fps1, fps2)
    shared_fps = len(fps1 & fps2)

    modifications: List[str] = []

    # Check for variable renaming indicators
    if similarity > 0.60:
        if vars1 != vars2:
            modifications.append("Variable/Identifier Renaming Detected")

    # Check for minor line/dead code insertions
    lines1 = len(code1.strip().splitlines())
    lines2 = len(code2.strip().splitlines())
    if similarity > 0.70 and abs(lines1 - lines2) > 2:
        modifications.append("Possible Dead Code / Dummy Statement Injection")

    return SimilarityResult(
        candidate_1=candidate_1_id,
        candidate_2=candidate_2_id,
        problem_id=problem_id,
        similarity_score=round(similarity, 4),
        shared_fingerprints_count=shared_fps,
        detected_modifications=modifications
    )
