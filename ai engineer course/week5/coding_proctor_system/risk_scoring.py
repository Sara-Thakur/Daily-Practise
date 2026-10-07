"""
Risk Scoring Module for Automated Coding Proctoring.

Combines MOSS structural similarity, Same Bug hidden-test failure pattern analysis,
and Judge LLM AI-generated code detection into a unified weighted risk probability (0.0 to 1.0).
Flags candidate submissions exceeding the risk threshold (0.70 / 70%) for manual investigation.
"""

from __future__ import annotations

from typing import List, Optional

from config import (
    AI_DETECTION_WEIGHT,
    BUG_SIMILARITY_WEIGHT,
    RISK_THRESHOLD,
    SIMILARITY_WEIGHT,
)
from models import (
    AIDetectionResult,
    RiskResult,
    SameBugResult,
    SimilarityResult,
)


def calculate_risk_score(
    candidate_id: str,
    problem_id: str,
    max_similarity_result: Optional[SimilarityResult],
    max_bug_result: Optional[SameBugResult],
    ai_detection_result: AIDetectionResult,
    similarity_weight: float = SIMILARITY_WEIGHT,
    bug_weight: float = BUG_SIMILARITY_WEIGHT,
    ai_weight: float = AI_DETECTION_WEIGHT,
    risk_threshold: float = RISK_THRESHOLD
) -> RiskResult:
    """
    Computes a weighted risk probability (0.0 to 1.0) for a candidate's submission.

    Formula:
      Risk = (w_sim * CodeSimilarity + w_bug * BugSimilarity + w_ai * (AI_Probability * AI_Confidence)) / (w_sim + w_bug + w_ai)

    Flags candidates for investigation if Risk > threshold (default 0.70).

    Args:
        candidate_id: Candidate identifier.
        problem_id: Problem identifier.
        max_similarity_result: SimilarityResult object with highest score against other candidates or AI.
        max_bug_result: SameBugResult object with highest score against other candidates.
        ai_detection_result: AIDetectionResult object from Groq LLM judge.
        similarity_weight: Weight for code structural similarity.
        bug_weight: Weight for hidden-test failure pattern similarity.
        ai_weight: Weight for AI detection probability.
        risk_threshold: Threshold above which candidate is flagged (> 0.70).

    Returns:
        RiskResult object containing aggregate score, component breakdown, collusion flags, and recommendations.
    """
    sim_score = max_similarity_result.similarity_score if max_similarity_result else 0.0
    bug_score = max_bug_result.same_bug_score if max_bug_result else 0.0

    # AI probability is confidence-weighted to reduce false alarms from uncertain judgments
    adjusted_ai_score = (
        ai_detection_result.probability * ai_detection_result.confidence
    )

    total_weights = similarity_weight + bug_weight + ai_weight
    if total_weights <= 0:
        total_weights = 1.0

    weighted_risk = (
        (similarity_weight * sim_score) +
        (bug_weight * bug_score) +
        (ai_weight * adjusted_ai_score)
    ) / total_weights

    # Bound risk between 0.0 and 1.0
    final_risk = round(max(0.0, min(1.0, weighted_risk)), 4)
    is_flagged = final_risk >= risk_threshold

    reasons: List[str] = []

    # Compile clear evidence justifications for proctors
    if max_similarity_result and max_similarity_result.similarity_score >= 0.70:
        partner = max_similarity_result.candidate_2
        reasons.append(
            f"High MOSS structural similarity ({max_similarity_result.similarity_score:.1%}) with submission '{partner}'"
        )
        if max_similarity_result.detected_modifications:
            mod_str = ", ".join(max_similarity_result.detected_modifications)
            reasons.append(f"Detected evasion techniques: {mod_str}")

    if max_bug_result and max_bug_result.is_collusion_suspect:
        partner = max_bug_result.candidate_2
        failed_str = ", ".join(max_bug_result.shared_failed_tests)
        reasons.append(
            f"Identical hidden-test failure pattern ({max_bug_result.same_bug_score:.1%}) with '{partner}' on tests [{failed_str}]"
        )

    if ai_detection_result.probability >= 0.60:
        reasons.append(
            f"Groq LLM Judge detected high AI characteristics (Probability: {ai_detection_result.probability:.1%}, Confidence: {ai_detection_result.confidence:.1%})"
        )
        for r in ai_detection_result.reasons[:2]:
            reasons.append(f"AI Observation: {r}")

    if not reasons:
        reasons.append("Clean submission with low structural similarity and normal test behavior.")

    # Determine recommendation status
    if final_risk >= 0.70:
        recommendation = "FLAGGED_FOR_INVESTIGATION"
    elif final_risk >= 0.45:
        recommendation = "MONITOR_MEDIUM_RISK"
    else:
        recommendation = "CLEAR"

    most_similar_cand = max_similarity_result.candidate_2 if max_similarity_result else "None"
    collusion_cand = max_bug_result.candidate_2 if (max_bug_result and max_bug_result.is_collusion_suspect) else "None"

    return RiskResult(
        candidate_id=candidate_id,
        problem_id=problem_id,
        overall_risk=final_risk,
        is_flagged=is_flagged,
        code_similarity_score=sim_score,
        most_similar_candidate=most_similar_cand,
        same_bug_score=bug_score,
        collusion_partner=collusion_cand,
        ai_probability=ai_detection_result.probability,
        reasons=reasons,
        recommendation=recommendation
    )
