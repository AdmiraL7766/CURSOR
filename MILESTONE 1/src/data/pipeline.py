"""Phase 1 pipeline runner."""

from __future__ import annotations

import argparse
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

from .clean import canonicalize
from .dedupe import dedupe_restaurants
from .ingest import fetch_dataset_with_retry
from .load import save_processed_csv, save_sqlite


def write_quality_report(report_path: Path, metrics: Dict[str, str | int]) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Phase 1 Data Quality Report",
        "",
        f"- Run ID: `{metrics['run_id']}`",
        f"- Timestamp (UTC): `{metrics['run_timestamp_utc']}`",
        f"- Data Source Status: `{metrics['data_source_status']}`",
        f"- Source Rows: `{metrics['source_rows']}`",
        f"- Invalid Rating Values: `{metrics['invalid_rating_values']}`",
        f"- Invalid Cost Values: `{metrics['invalid_cost_values']}`",
        f"- Dropped Missing Required: `{metrics['dropped_missing_required']}`",
        f"- Duplicate Rows Removed: `{metrics['duplicates_removed']}`",
        f"- Final Usable Rows: `{metrics['final_rows']}`",
    ]
    report_path.write_text("\n".join(lines), encoding="utf-8")


def run_pipeline(project_root: Path, dataset_id: str) -> Dict[str, str | int]:
    raw_dir = project_root / "data" / "raw"
    processed_dir = project_root / "data" / "processed"
    report_path = project_root / "data" / "reports" / "phase1_data_quality.md"

    run_id = str(uuid.uuid4())
    run_ts = datetime.now(timezone.utc).isoformat(timespec="seconds")

    raw_frame, source_status = fetch_dataset_with_retry(dataset_id=dataset_id, raw_dir=raw_dir)
    cleaned_frame, metrics = canonicalize(raw_frame)
    deduped_frame, duplicates_removed = dedupe_restaurants(cleaned_frame)

    csv_path = save_processed_csv(deduped_frame, processed_dir=processed_dir)

    final_metrics: Dict[str, str | int] = {
        "run_id": run_id,
        "run_timestamp_utc": run_ts,
        "data_source_status": source_status,
        "source_rows": int(metrics["source_rows"]),
        "invalid_rating_values": int(metrics["invalid_rating_values"]),
        "invalid_cost_values": int(metrics["invalid_cost_values"]),
        "dropped_missing_required": int(metrics["dropped_missing_required"]),
        "duplicates_removed": int(duplicates_removed),
        "final_rows": int(len(deduped_frame)),
        "processed_csv_path": str(csv_path),
    }
    sqlite_path = save_sqlite(deduped_frame, processed_dir=processed_dir, metadata=final_metrics)
    final_metrics["processed_sqlite_path"] = str(sqlite_path)

    write_quality_report(report_path=report_path, metrics=final_metrics)
    final_metrics["quality_report_path"] = str(report_path)
    return final_metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Phase 1 data foundation pipeline.")
    parser.add_argument(
        "--dataset-id",
        default="ManikaSaini/zomato-restaurant-recommendation",
        help="Hugging Face dataset identifier.",
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root path where data/ directory will be created.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metrics = run_pipeline(project_root=Path(args.project_root).resolve(), dataset_id=args.dataset_id)
    print("Phase 1 pipeline completed.")
    print(f"Final usable rows: {metrics['final_rows']}")
    print(f"CSV: {metrics['processed_csv_path']}")
    print(f"SQLite: {metrics['processed_sqlite_path']}")
    print(f"Report: {metrics['quality_report_path']}")


if __name__ == "__main__":
    main()
