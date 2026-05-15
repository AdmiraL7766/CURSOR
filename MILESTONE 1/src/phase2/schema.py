"""Preference schema for standardized user input."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass
class PreferenceInput:
    """Structured, validated user preference object."""

    location: str
    budget_tier: str
    cuisine: str
    min_rating: float
    additional_preferences: List[str] = field(default_factory=list)
    original_budget_input: str | None = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

