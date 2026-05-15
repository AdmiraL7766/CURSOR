"""Canonical schema and source column mapping utilities."""

from __future__ import annotations

from typing import Dict, Iterable, List

CANONICAL_FIELDS: List[str] = [
    "restaurant_id",
    "name",
    "location",
    "cuisine",
    "cost_for_two",
    "rating",
    "is_active",
    "source_updated_at",
    "ingested_at",
]

REQUIRED_FIELDS: List[str] = ["name", "location", "cuisine", "cost_for_two", "rating"]

# Candidate source columns by canonical key, ordered by preference.
SOURCE_CANDIDATES: Dict[str, List[str]] = {
    "restaurant_id": ["restaurant_id", "res_id", "id"],
    "name": ["restaurant_name", "name", "res_name", "title"],
    "location": ["location", "city", "area", "address"],
    "cuisine": ["cuisines", "cuisine", "food_type"],
    "cost_for_two": [
        "average_cost_for_two",
        "cost_for_two",
        "price_for_two",
        "cost",
        "approx_cost(for two people)",
    ],
    "rating": ["aggregate_rating", "rating", "user_rating", "rate"],
    "is_active": ["is_active", "active", "status"],
    "source_updated_at": ["updated_at", "last_updated", "source_updated_at"],
}


def resolve_column_map(columns: Iterable[str]) -> Dict[str, str]:
    """Resolve canonical field -> source column using configured candidates."""
    normalized = {column.strip().lower(): column for column in columns}
    mapping: Dict[str, str] = {}
    for canonical, candidates in SOURCE_CANDIDATES.items():
        for candidate in candidates:
            source = normalized.get(candidate.lower())
            if source:
                mapping[canonical] = source
                break
    return mapping
