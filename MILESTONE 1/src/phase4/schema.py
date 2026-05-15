"""Schema contracts for Phase 4 recommendation outputs."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass
class RecommendationItem:
    restaurant_id: str
    name: str
    cuisine: str
    rating: float
    cost_for_two: float
    rank: int
    explanation: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RecommendationResult:
    preferences: Dict[str, Any]
    recommendations: List[RecommendationItem] = field(default_factory=list)
    summary: str = ""
    llm_mode: str = "fallback"
    llm_provider: str = "local"
    candidate_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "preferences": self.preferences,
            "recommendations": [item.to_dict() for item in self.recommendations],
            "summary": self.summary,
            "llm_mode": self.llm_mode,
            "llm_provider": self.llm_provider,
            "candidate_count": self.candidate_count,
        }

