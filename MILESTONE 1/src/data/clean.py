"""Data cleaning, normalization, and schema validation."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Dict, Tuple

import pandas as pd

from .schema import REQUIRED_FIELDS, resolve_column_map


def _normalize_text(value: object) -> str | None:
    if pd.isna(value):
        return None
    text = str(value).strip()
    return re.sub(r"\s+", " ", text) if text else None


def _parse_numeric(value: object) -> float | None:
    if pd.isna(value):
        return None
    text = str(value)
    match = re.findall(r"\d+(?:\.\d+)?", text.replace(",", ""))
    if not match:
        return None
    return float(match[0])


def canonicalize(raw: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int | str]]:
    """Map source columns to canonical schema and normalize values."""
    column_map = resolve_column_map(raw.columns)
    report: Dict[str, int | str] = {"source_rows": int(len(raw))}

    working = pd.DataFrame()
    for canonical, source in column_map.items():
        working[canonical] = raw[source]

    if "restaurant_id" not in working:
        working["restaurant_id"] = [f"gen_{idx}" for idx in range(1, len(working) + 1)]
    if "is_active" not in working:
        working["is_active"] = True
    if "source_updated_at" not in working:
        working["source_updated_at"] = None

    working["name"] = working["name"].map(_normalize_text) if "name" in working else None
    working["location"] = (
        working["location"].map(_normalize_text) if "location" in working else None
    )
    working["cuisine"] = working["cuisine"].map(_normalize_text) if "cuisine" in working else None
    working["cost_for_two"] = (
        working["cost_for_two"].map(_parse_numeric) if "cost_for_two" in working else None
    )
    working["rating"] = working["rating"].map(_parse_numeric) if "rating" in working else None
    working["is_active"] = working["is_active"].fillna(True).astype(bool)
    working["ingested_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

    missing_required_columns = [field for field in REQUIRED_FIELDS if field not in working.columns]
    if missing_required_columns:
        raise ValueError(f"Missing required mapped columns: {missing_required_columns}")

    invalid_rating = ~working["rating"].between(0.0, 5.0, inclusive="both")
    working.loc[invalid_rating, "rating"] = None
    report["invalid_rating_values"] = int(invalid_rating.sum())

    invalid_cost = working["cost_for_two"] <= 0
    working.loc[invalid_cost, "cost_for_two"] = None
    report["invalid_cost_values"] = int(invalid_cost.sum())

    pre_drop_rows = len(working)
    working = working.dropna(subset=REQUIRED_FIELDS)
    report["dropped_missing_required"] = int(pre_drop_rows - len(working))
    report["rows_after_validation"] = int(len(working))

    # Derive budget tier so downstream phases don't need to recompute it.
    working["budget_tier"] = working["cost_for_two"].apply(_cost_to_budget_tier)

    return working, report


def _cost_to_budget_tier(cost_for_two: float) -> str:
    """Map cost_for_two to a budget tier label."""
    if cost_for_two < 600:
        return "low"
    if cost_for_two <= 1500:
        return "medium"
    return "high"
