"""Deduplication helpers for restaurant records."""

from __future__ import annotations

import pandas as pd


def dedupe_restaurants(frame: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Remove duplicates by normalized name/location/cuisine signature."""
    working = frame.copy()
    working["_dedupe_key"] = (
        working["name"].str.lower().str.strip()
        + "|"
        + working["location"].str.lower().str.strip()
        + "|"
        + working["cuisine"].str.lower().str.strip()
    )
    working = working.sort_values(by=["rating", "cost_for_two"], ascending=[False, True])
    deduped = working.drop_duplicates(subset=["_dedupe_key"], keep="first").drop(
        columns=["_dedupe_key"]
    )
    removed = len(frame) - len(deduped)
    return deduped.reset_index(drop=True), int(removed)
