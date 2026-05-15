"""Phase 3 pipeline entrypoint."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

import pandas as pd

from .retrieval import RetrievalConfig, retrieve_candidates


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Phase 3 candidate retrieval.")
    parser.add_argument(
        "--restaurants-csv",
        default="data/processed/restaurants_clean.csv",
        help="Path to Phase 1 cleaned restaurants CSV.",
    )
    parser.add_argument(
        "--preferences-json",
        default="data/processed/phase2_preference.json",
        help="Path to Phase 2 validated preference JSON.",
    )
    parser.add_argument(
        "--output-json",
        default="data/processed/phase3_candidates.json",
        help="Output path for retrieved candidates JSON.",
    )
    parser.add_argument(
        "--max-candidates",
        type=int,
        default=30,
        help="Maximum candidates to return after pre-scoring.",
    )
    return parser.parse_args()


def load_preferences(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Preferences file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def run_pipeline(
    restaurants_csv: Path,
    preferences_json: Path,
    output_json: Path,
    max_candidates: int = 30,
) -> Dict[str, Any]:
    if not restaurants_csv.exists():
        raise FileNotFoundError(f"Restaurants CSV not found: {restaurants_csv}")

    restaurants = pd.read_csv(restaurants_csv)
    if "budget_tier" not in restaurants.columns:
        # Derive budget tier for backward compatibility with Phase 1 outputs.
        costs = pd.to_numeric(restaurants["cost_for_two"], errors="coerce").fillna(0.0)
        restaurants["budget_tier"] = costs.apply(_cost_to_budget_tier)

    preferences = load_preferences(preferences_json)
    config = RetrievalConfig(max_candidates=max_candidates)
    result = retrieve_candidates(restaurants, preferences, config=config).to_dict()

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def _cost_to_budget_tier(cost_for_two: float) -> str:
    if cost_for_two < 600:
        return "low"
    if cost_for_two <= 1500:
        return "medium"
    return "high"


def main() -> None:
    args = parse_args()
    result = run_pipeline(
        restaurants_csv=Path(args.restaurants_csv),
        preferences_json=Path(args.preferences_json),
        output_json=Path(args.output_json),
        max_candidates=args.max_candidates,
    )
    print("Phase 3 pipeline completed.")
    print(f"Candidates returned: {len(result.get('candidates', []))}")
    print(f"Fallback steps used: {result.get('fallback_steps_used', [])}")
    print(f"Output: {args.output_json}")


if __name__ == "__main__":
    main()

