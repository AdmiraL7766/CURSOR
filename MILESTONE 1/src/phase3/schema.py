"""Schema objects for Phase 3 candidate retrieval."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass
class CandidateRetrievalResult:
    """Output contract for filtered candidates and retrieval metadata."""

    preferences: Dict[str, Any]
    candidates: List[Dict[str, Any]]
    fallback_steps_used: List[str] = field(default_factory=list)
    total_candidates_before_cap: int = 0
    max_candidates: int = 30

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

