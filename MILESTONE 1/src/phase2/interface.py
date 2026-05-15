"""Input interfaces for phase 2 preference capture."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from .schema import PreferenceInput
from .validators import validate_preferences


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Capture and validate recommendation preferences.")
    parser.add_argument("--location", required=True, help="Preferred location (e.g., Delhi).")
    parser.add_argument("--budget", required=True, help="Budget tier or amount (e.g., low, 800).")
    parser.add_argument("--cuisine", required=True, help="Preferred cuisine.")
    parser.add_argument("--min-rating", required=True, help="Minimum rating between 0 and 5.")
    parser.add_argument(
        "--additional-preference",
        action="append",
        default=[],
        help="Additional preference. Repeat flag to add multiple values.",
    )
    parser.add_argument(
        "--output-json",
        default="",
        help="Optional path to save validated preference object as JSON.",
    )
    return parser


def from_payload(payload: Dict[str, Any]) -> PreferenceInput:
    return validate_preferences(
        location=str(payload.get("location", "")),
        budget=str(payload.get("budget", "")),
        cuisine=str(payload.get("cuisine", "")),
        min_rating=payload.get("min_rating", ""),
        additional_preferences=payload.get("additional_preferences", []),
    )


def run_cli() -> None:
    parser = build_parser()
    args = parser.parse_args()

    preference = validate_preferences(
        location=args.location,
        budget=args.budget,
        cuisine=args.cuisine,
        min_rating=args.min_rating,
        additional_preferences=args.additional_preference,
    )

    output = preference.to_dict()
    print(json.dumps(output, indent=2))

    if args.output_json:
        target = Path(args.output_json)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(output, indent=2), encoding="utf-8")

