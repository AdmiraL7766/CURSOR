"""Rule-based candidate retrieval with fallback strategy."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import pandas as pd

from .schema import CandidateRetrievalResult


@dataclass
class RetrievalConfig:
    max_candidates: int = 30
    rating_relax_step: float = 0.5
    max_rating_relax_steps: int = 2
    budget_expand_order: Tuple[str, ...] = ("medium", "low", "high")
    location_expand_enabled: bool = True


BUDGET_TIER_ORDER = {"low": 0, "medium": 1, "high": 2}

LOCATION_NEARBY_MAP: Dict[str, List[str]] = {
    "Delhi": ["Gurgaon", "Noida", "Faridabad"],
    "Bangalore": ["Whitefield", "Electronic City", "Indiranagar"],
    "Mumbai": ["Navi Mumbai", "Thane"],
}


def retrieve_candidates(
    restaurants: pd.DataFrame,
    preferences: Dict[str, Any],
    config: RetrievalConfig | None = None,
) -> CandidateRetrievalResult:
    cfg = config or RetrievalConfig()

    working = restaurants.copy()
    required = {"location", "budget_tier", "cuisine", "min_rating"}
    missing = sorted(required - set(preferences))
    if missing:
        raise ValueError(f"Missing preference fields: {missing}")

    base_location = str(preferences["location"]).strip()
    base_budget = str(preferences["budget_tier"]).strip().lower()
    base_cuisine = str(preferences["cuisine"]).strip().lower()
    base_min_rating = float(preferences["min_rating"])

    if base_budget not in BUDGET_TIER_ORDER:
        raise ValueError("budget_tier must be one of: low, medium, high.")

    fallback_steps: List[str] = []
    filtered = _apply_filters(
        working,
        location=base_location,
        budget_tier=base_budget,
        cuisine=base_cuisine,
        min_rating=base_min_rating,
    )

    # Fallback 1: relax rating threshold if no matches.
    if filtered.empty:
        current_rating = base_min_rating
        for _ in range(cfg.max_rating_relax_steps):
            current_rating = max(0.0, round(current_rating - cfg.rating_relax_step, 2))
            filtered = _apply_filters(
                working,
                location=base_location,
                budget_tier=base_budget,
                cuisine=base_cuisine,
                min_rating=current_rating,
            )
            fallback_steps.append(f"relax_rating_to_{current_rating}")
            if not filtered.empty:
                break

    # Fallback 2: widen budget tier scope if still empty.
    if filtered.empty:
        for expanded_budget in _expand_budget(base_budget, cfg.budget_expand_order):
            filtered = _apply_filters(
                working,
                location=base_location,
                budget_tier=expanded_budget,
                cuisine=base_cuisine,
                min_rating=base_min_rating,
            )
            fallback_steps.append(f"expand_budget_to_{expanded_budget}")
            if not filtered.empty:
                break

    # Fallback 3: include nearby locations if still empty.
    if filtered.empty and cfg.location_expand_enabled:
        nearby_locations = LOCATION_NEARBY_MAP.get(base_location, [])
        for nearby in nearby_locations:
            filtered = _apply_filters(
                working,
                location=nearby,
                budget_tier=base_budget,
                cuisine=base_cuisine,
                min_rating=base_min_rating,
            )
            fallback_steps.append(f"expand_location_to_{nearby}")
            if not filtered.empty:
                break

    scored = _prescore_candidates(filtered, preferences)
    total_before_cap = len(scored)
    top = scored.head(cfg.max_candidates)

    # Remove internal scoring columns before output
    internal_cols = [c for c in top.columns if c.startswith("_")]
    if internal_cols:
        top = top.drop(columns=internal_cols)

    return CandidateRetrievalResult(
        preferences=preferences,
        candidates=top.to_dict(orient="records"),
        fallback_steps_used=fallback_steps,
        total_candidates_before_cap=int(total_before_cap),
        max_candidates=cfg.max_candidates,
    )


def _apply_filters(
    frame: pd.DataFrame,
    *,
    location: str,
    budget_tier: str,
    cuisine: str,
    min_rating: float,
) -> pd.DataFrame:
    filtered = frame.copy()
    filtered = filtered[filtered["location"].astype(str).str.contains(location, case=False, na=False)]
    filtered = filtered[filtered["budget_tier"].astype(str).str.lower() == budget_tier]
    if cuisine.lower() != "any":
        filtered = filtered[filtered["cuisine"].astype(str).str.contains(cuisine, case=False, na=False)]
    filtered = filtered[pd.to_numeric(filtered["rating"], errors="coerce") >= min_rating]
    return filtered


def _expand_budget(base_budget: str, budget_expand_order: Tuple[str, ...]) -> List[str]:
    remaining = [tier for tier in budget_expand_order if tier != base_budget]
    return [base_budget] + remaining


def _prescore_candidates(frame: pd.DataFrame, preferences: Dict[str, Any]) -> pd.DataFrame:
    if frame.empty:
        return frame
    working = frame.copy()

    target_rating = float(preferences["min_rating"])
    target_budget = str(preferences["budget_tier"]).strip().lower()

    working["rating"] = pd.to_numeric(working["rating"], errors="coerce").fillna(0.0)
    working["cost_for_two"] = pd.to_numeric(working["cost_for_two"], errors="coerce").fillna(0.0)

    # Weighted score favors better ratings and budget proximity.
    working["_rating_score"] = (working["rating"] - target_rating).clip(lower=0) + working["rating"]
    working["_budget_distance"] = (
        working["budget_tier"].astype(str).str.lower().map(BUDGET_TIER_ORDER).fillna(99)
        - BUDGET_TIER_ORDER[target_budget]
    ).abs()
    working["_cost_score"] = (1 / (1 + working["cost_for_two"])).fillna(0.0)
    working["_pre_score"] = (
        0.7 * working["_rating_score"] + 0.2 * (1 / (1 + working["_budget_distance"])) + 0.1 * working["_cost_score"]
    )

    working = working.sort_values(
        by=["_pre_score", "rating", "cost_for_two"], ascending=[False, False, True]
    )
    return working.drop(columns=["_rating_score", "_budget_distance", "_cost_score"])

