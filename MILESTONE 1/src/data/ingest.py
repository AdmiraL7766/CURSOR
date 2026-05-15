"""Dataset ingestion and raw snapshot management."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple

import pandas as pd
from datasets import load_dataset


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def latest_snapshot(raw_dir: Path) -> Path | None:
    snapshots = sorted(raw_dir.glob("zomato_*.csv"))
    return snapshots[-1] if snapshots else None


def fetch_dataset_with_retry(
    dataset_id: str,
    raw_dir: Path,
    retries: int = 3,
    backoff_seconds: int = 2,
) -> Tuple[pd.DataFrame, str]:
    """Fetch dataset and save raw snapshot, with fallback to latest snapshot."""
    ensure_dir(raw_dir)
    last_error: Exception | None = None

    for attempt in range(1, retries + 1):
        try:
            split = load_dataset(dataset_id, split="train")
            frame = split.to_pandas()
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            snapshot = raw_dir / f"zomato_{timestamp}.csv"
            frame.to_csv(snapshot, index=False)
            return frame, f"downloaded:{snapshot.name}"
        except Exception as exc:  # pragma: no cover - network/runtime failure path
            last_error = exc
            if attempt < retries:
                time.sleep(backoff_seconds * attempt)

    snapshot = latest_snapshot(raw_dir)
    if snapshot is not None:
        frame = pd.read_csv(snapshot)
        return frame, f"fallback_snapshot:{snapshot.name}"

    message = "Failed to fetch dataset and no snapshot available."
    if last_error is not None:
        message = f"{message} Last error: {last_error}"
    raise RuntimeError(message)
