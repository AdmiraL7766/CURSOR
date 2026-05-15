"""Schema contracts for Phase 5 response formatting."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass
class RecommendationCard:
    """UI-friendly recommendation view model."""

    rank: int
    restaurant_id: str
    title: str
    cuisine: str
    rating: float
    estimated_cost_for_two: float
    explanation: str
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FinalResponsePayload:
    """Final API response contract for presentation layer."""

    status: str
    message: str
    preferences: Dict[str, Any]
    summary: str
    recommendations: List[RecommendationCard] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "message": self.message,
            "preferences": self.preferences,
            "summary": self.summary,
            "recommendations": [r.to_dict() for r in self.recommendations],
            "metadata": self.metadata,
        }

