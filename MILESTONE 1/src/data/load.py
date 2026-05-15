"""Persist processed data and metadata."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict

import pandas as pd


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def save_processed_csv(frame: pd.DataFrame, processed_dir: Path) -> Path:
    ensure_dir(processed_dir)
    target = processed_dir / "restaurants_clean.csv"
    frame.to_csv(target, index=False)
    return target


def save_sqlite(frame: pd.DataFrame, processed_dir: Path, metadata: Dict[str, str | int]) -> Path:
    ensure_dir(processed_dir)
    target = processed_dir / "restaurants.db"
    conn = sqlite3.connect(target)
    try:
        frame.to_sql("restaurants_clean", conn, if_exists="replace", index=False)
        metadata_frame = pd.DataFrame([metadata])
        metadata_frame.to_sql("ingestion_runs", conn, if_exists="append", index=False)
    finally:
        conn.close()
    return target
