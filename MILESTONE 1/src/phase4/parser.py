"""Parse and validate recommendation output from LLM/fallback."""

from __future__ import annotations

import json
from typing import Any, Dict, List

from .schema import RecommendationItem


def parse_recommendation_json(raw_content: str) -> Dict[str, Any]:
    if not raw_content.strip():
        raise ValueError("Empty LLM output.")
    payload = json.loads(raw_content)
    if "recommendations" not in payload or not isinstance(payload["recommendations"], list):
        raise ValueError("LLM output missing 'recommendations' list.")
    if "summary" not in payload:
        payload["summary"] = ""
    return payload


def validate_recommendations(
    parsed_payload: Dict[str, Any],
    candidate_index: Dict[str, Dict[str, Any]],
    top_n: int,
) -> List[RecommendationItem]:
    valid_items: List[RecommendationItem] = []
    used_ids = set()

    for idx, raw_item in enumerate(parsed_payload.get("recommendations", []), start=1):
        rid = str(raw_item.get("restaurant_id", "")).strip()
        if not rid or rid in used_ids or rid not in candidate_index:
            continue

        candidate = candidate_index[rid]
        explanation = str(raw_item.get("explanation", "")).strip()
        if not explanation:
            explanation = _default_explanation(candidate)

        valid_items.append(
            RecommendationItem(
                restaurant_id=rid,
                name=str(candidate.get("name", "")),
                cuisine=str(candidate.get("cuisine", "")),
                rating=float(candidate.get("rating", 0.0)),
                cost_for_two=float(candidate.get("cost_for_two", 0.0)),
                rank=idx,
                explanation=explanation,
            )
        )
        used_ids.add(rid)
        if len(valid_items) >= top_n:
            break

    return valid_items


def _default_explanation(candidate: Dict[str, Any]) -> str:
    return (
        f"Good fit based on cuisine match, rating {candidate.get('rating', 'N/A')}, "
        f"and estimated cost for two around {candidate.get('cost_for_two', 'N/A')}."
    )

