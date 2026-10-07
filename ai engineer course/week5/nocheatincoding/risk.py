"""Risk aggregation for coding-integrity review."""

from __future__ import annotations

from typing import Dict

from .models import AIDetectionResult, RiskResult


def combine_risk(
    similarity_score: float,
    bug_similarity_score: float,
    ai_result: AIDetectionResult,
    *,
    similarity_weight: float = 0.40,
    bug_weight: float = 0.40,
    ai_weight: float = 0.20,
) -> RiskResult:
    """
    Combine multiple signals into a bounded review-risk probability.

    This is a triage score, not a determination of misconduct.

    Args:
        similarity_score: Similarity to another submission, [0, 1].
        bug_similarity_score: Similarity of hidden-test behavior, [0, 1].
        ai_result: LLM-based AI-characteristics assessment.
        similarity_weight: Weight assigned to code similarity.
        bug_weight: Weight assigned to bug similarity.
        ai_weight: Weight assigned to AI-characteristics evidence.

    Returns:
        Aggregate RiskResult.
    """
    weights = [
        similarity_weight,
        bug_weight,
        ai_weight,
    ]

    if any(weight < 0 for weight in weights):
        raise ValueError("Risk weights cannot be negative")

    total_weight = sum(weights)

    if total_weight == 0:
        raise ValueError("At least one risk weight must be positive")

    similarity_score = max(0.0, min(1.0, similarity_score))
    bug_similarity_score = max(0.0, min(1.0, bug_similarity_score))

    # Confidence-adjust the LLM signal so an uncertain judge contributes less.
    adjusted_ai_score = (
        ai_result.probability *
        ai_result.confidence
    )

    probability = (
        similarity_weight * similarity_score
        + bug_weight * bug_similarity_score
        + ai_weight * adjusted_ai_score
    ) / total_weight

    return RiskResult(
        probability=max(0.0, min(1.0, probability)),
        components={
            "code_similarity": similarity_score,
            "bug_similarity": bug_similarity_score,
            "ai_characteristics": adjusted_ai_score,
        },
        evidence={
            "ai_reasons": ai_result.reasons,
            "baseline_matches": ai_result.baseline_matches,
            "ai_confidence": ai_result.confidence,
        },
    )
