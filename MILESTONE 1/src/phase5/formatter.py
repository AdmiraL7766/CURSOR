"""Response formatter for Phase 5 payloads."""

from __future__ import annotations

from typing import Any, Dict, List

from .schema import FinalResponsePayload, RecommendationCard


def format_final_response(phase4_payload: Dict[str, Any], top_n: int = 5) -> FinalResponsePayload:
    preferences = phase4_payload.get("preferences", {})
    summary = str(phase4_payload.get("summary", "")).strip()
    llm_mode = str(phase4_payload.get("llm_mode", "fallback"))
    llm_provider = str(phase4_payload.get("llm_provider", "local"))
    candidate_count = int(phase4_payload.get("candidate_count", 0))
    recs = phase4_payload.get("recommendations", [])

    cards: List[RecommendationCard] = []
    for item in recs[:top_n]:
        rank = int(item.get("rank", len(cards) + 1))
        title = str(item.get("name", "")).strip() or "Unknown Restaurant"
        cuisine = str(item.get("cuisine", "Unknown")).strip() or "Unknown"
        rating = _to_float(item.get("rating", 0.0))
        cost = _to_float(item.get("cost_for_two", 0.0))
        explanation = str(item.get("explanation", "")).strip()
        if not explanation:
            explanation = "Recommended based on your preferences and candidate quality."

        cards.append(
            RecommendationCard(
                rank=rank,
                restaurant_id=str(item.get("restaurant_id", "")).strip(),
                title=title,
                cuisine=cuisine,
                rating=rating,
                estimated_cost_for_two=cost,
                explanation=explanation,
                tags=_build_tags(rating=rating, cost=cost, llm_mode=llm_mode),
            )
        )

    if not summary:
        summary = _default_summary(cards, preferences)

    message = "Recommendations generated successfully." if cards else "No recommendations found."
    status = "success" if cards else "empty"
    metadata = {
        "top_n_requested": top_n,
        "recommendations_returned": len(cards),
        "llm_mode": llm_mode,
        "llm_provider": llm_provider,
        "candidate_count_received": candidate_count,
    }

    return FinalResponsePayload(
        status=status,
        message=message,
        preferences=preferences,
        summary=summary,
        recommendations=cards,
        metadata=metadata,
    )


def _build_tags(*, rating: float, cost: float, llm_mode: str) -> List[str]:
    tags: List[str] = []
    if rating >= 4.5:
        tags.append("top-rated")
    elif rating >= 4.0:
        tags.append("high-rated")
    if cost > 0 and cost < 600:
        tags.append("budget-friendly")
    elif cost > 1500:
        tags.append("premium")
    if llm_mode == "fallback":
        tags.append("fallback-ranked")
    return tags


def _default_summary(cards: List[RecommendationCard], preferences: Dict[str, Any]) -> str:
    if not cards:
        return "No restaurants matched your preferences. Try relaxing one or more filters."
    cuisine = preferences.get("cuisine", "your preferred cuisine")
    location = preferences.get("location", "your selected location")
    return f"Top {len(cards)} {cuisine} options in {location}, ranked by fit and quality."


def _to_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0

