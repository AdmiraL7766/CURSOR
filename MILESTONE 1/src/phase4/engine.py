"""Recommendation engine orchestration for Phase 4."""

from __future__ import annotations

import json
from typing import Any, Dict, List

from .llm_service import call_llm
from .parser import parse_recommendation_json, validate_recommendations
from .prompt_builder import build_recommendation_prompt
from .schema import RecommendationItem, RecommendationResult


def generate_recommendations(
    *,
    preferences: Dict[str, Any],
    candidates: List[Dict[str, Any]],
    top_n: int = 5,
) -> RecommendationResult:
    trimmed_candidates = candidates[: max(top_n * 3, top_n)]
    prompt = build_recommendation_prompt(preferences, trimmed_candidates)
    llm_response = call_llm(prompt, top_n=top_n)

    candidate_index = _candidate_index(trimmed_candidates)

    recommendations: List[RecommendationItem] = []
    summary = ""
    mode = str(llm_response.get("mode", "fallback"))
    provider = str(llm_response.get("provider", "local"))

    if mode == "remote":
        try:
            parsed = parse_recommendation_json(str(llm_response.get("raw_content", "")))
            recommendations = validate_recommendations(parsed, candidate_index, top_n=top_n)
            summary = str(parsed.get("summary", "")).strip()
        except (ValueError, json.JSONDecodeError):
            recommendations = []

    if not recommendations:
        recommendations = _fallback_rank(trimmed_candidates, top_n=top_n)
        summary = (
            "Recommendations generated using deterministic fallback ranking "
            "because remote LLM output was unavailable or invalid."
        )
        mode = "fallback"
        provider = "local"

    return RecommendationResult(
        preferences=preferences,
        recommendations=recommendations,
        summary=summary,
        llm_mode=mode,
        llm_provider=provider,
        candidate_count=len(candidates),
    )


def _candidate_index(candidates: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    index: Dict[str, Dict[str, Any]] = {}
    for row in candidates:
        rid = str(row.get("restaurant_id", "")).strip()
        if rid:
            index[rid] = row
    return index


def _fallback_rank(candidates: List[Dict[str, Any]], top_n: int) -> List[RecommendationItem]:
    sorted_rows = sorted(
        candidates,
        key=lambda row: (
            float(row.get("rating", 0.0)),
            -float(row.get("cost_for_two", 0.0)),
        ),
        reverse=True,
    )
    output: List[RecommendationItem] = []
    for rank, row in enumerate(sorted_rows[:top_n], start=1):
        output.append(
            RecommendationItem(
                restaurant_id=str(row.get("restaurant_id", "")),
                name=str(row.get("name", "")),
                cuisine=str(row.get("cuisine", "")),
                rating=float(row.get("rating", 0.0)),
                cost_for_two=float(row.get("cost_for_two", 0.0)),
                rank=rank,
                explanation=(
                    f"Recommended for strong rating ({row.get('rating', 'N/A')}) and cuisine fit "
                    f"within your expected budget profile."
                ),
            )
        )
    return output

