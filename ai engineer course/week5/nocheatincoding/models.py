"""Shared data models for the coding-proctoring pipeline."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SimilarityResult:
    """Represent structural similarity between two submissions."""

    student_id: str
    comparison_id: str
    similarity: float
    shared_fingerprints: int


@dataclass
class BugPattern:
    """Represent the observable test-case failure pattern of a submission."""

    student_id: str
    failures: List[bool]
    error_types: List[Optional[str]]
    outputs: List[Optional[str]] = field(default_factory=list)


@dataclass
class AIDetectionResult:
    """Represent an LLM-based assessment of AI-generated-code indicators."""

    probability: float
    confidence: float
    reasons: List[str]
    baseline_matches: List[str] = field(default_factory=list)


@dataclass
class RiskResult:
    """Represent the aggregate risk assessment."""

    probability: float
    components: Dict[str, float]
    evidence: Dict[str, Any]
