"""Validation and normalization rules for preference capture."""

from __future__ import annotations

import re
from typing import Iterable, List, Tuple

from .schema import PreferenceInput

VALID_BUDGET_TIERS = {"low", "medium", "high"}

BUDGET_ALIASES = {
    "cheap": "low",
    "budget": "low",
    "affordable": "low",
    "moderate": "medium",
    "mid": "medium",
    "midrange": "medium",
    "premium": "high",
    "expensive": "high",
    "luxury": "high",
}

LOCATION_ALIASES = {
    "blr": "Bangalore",
    "banglore": "Bangalore",
    "bengaluru": "Bangalore",
    "delhi ncr": "Delhi",
    "new delhi": "Delhi",
    "mum": "Mumbai",
    "bombay": "Mumbai",
}


def normalize_location(raw_location: str) -> str:
    location = re.sub(r"\s+", " ", raw_location.strip())
    if not location:
        raise ValueError("Location is required.")
    mapped = LOCATION_ALIASES.get(location.lower(), location)
    return mapped.title() if mapped.islower() else mapped


def normalize_budget(raw_budget: str) -> Tuple[str, str]:
    budget = raw_budget.strip().lower()
    if not budget:
        raise ValueError("Budget is required.")

    if budget in VALID_BUDGET_TIERS:
        return budget, raw_budget

    if budget in BUDGET_ALIASES:
        return BUDGET_ALIASES[budget], raw_budget

    numeric = _extract_numeric_budget(budget)
    if numeric is not None:
        # Cost thresholds for two people.
        if numeric < 600:
            return "low", raw_budget
        if numeric <= 1500:
            return "medium", raw_budget
        return "high", raw_budget

    raise ValueError(
        "Invalid budget. Supported values: low, medium, high, common aliases, or numeric amount."
    )


def normalize_cuisine(raw_cuisine: str) -> str:
    cuisine = re.sub(r"\s+", " ", raw_cuisine.strip())
    if not cuisine:
        raise ValueError("Cuisine is required.")
    return cuisine.title()


def normalize_rating(raw_rating: str | float | int) -> float:
    if isinstance(raw_rating, (int, float)):
        rating = float(raw_rating)
    else:
        text = raw_rating.strip()
        if not text:
            raise ValueError("Minimum rating is required.")
        try:
            rating = float(text)
        except ValueError as exc:
            raise ValueError("Minimum rating must be a number between 0 and 5.") from exc

    if rating < 0 or rating > 5:
        raise ValueError("Minimum rating must be in range [0, 5].")
    return round(rating, 1)


def normalize_additional_preferences(raw_values: Iterable[str] | None) -> List[str]:
    if not raw_values:
        return []
    normalized: List[str] = []
    for value in raw_values:
        text = re.sub(r"\s+", " ", value.strip())
        if text:
            normalized.append(text.lower())
    # Preserve input order while removing duplicates.
    unique = list(dict.fromkeys(normalized))
    return unique


def validate_preferences(
    *,
    location: str,
    budget: str,
    cuisine: str,
    min_rating: str | float | int,
    additional_preferences: Iterable[str] | None = None,
) -> PreferenceInput:
    normalized_location = normalize_location(location)
    budget_tier, original_budget = normalize_budget(budget)
    normalized_cuisine = normalize_cuisine(cuisine)
    normalized_rating = normalize_rating(min_rating)
    normalized_additional = normalize_additional_preferences(additional_preferences)

    return PreferenceInput(
        location=normalized_location,
        budget_tier=budget_tier,
        cuisine=normalized_cuisine,
        min_rating=normalized_rating,
        additional_preferences=normalized_additional,
        original_budget_input=original_budget,
    )


def _extract_numeric_budget(value: str) -> float | None:
    numbers = re.findall(r"\d+(?:\.\d+)?", value.replace(",", ""))
    if not numbers:
        return None
    return float(numbers[0])

