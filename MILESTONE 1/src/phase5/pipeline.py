"""Phase 5 pipeline entrypoint."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from .formatter import format_final_response


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Phase 5 response and presentation formatting.")
    parser.add_argument(
        "--phase4-json",
        default="data/processed/phase4_recommendations.json",
        help="Input JSON from Phase 4 recommendation layer.",
    )
    parser.add_argument(
        "--output-json",
        default="data/processed/final_response.json",
        help="Output path for final response payload.",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=5,
        help="Maximum recommendations to include in final payload.",
    )
    return parser.parse_args()


def run_pipeline(phase4_json: Path, output_json: Path, top_n: int = 5) -> Dict[str, Any]:
    if not phase4_json.exists():
        raise FileNotFoundError(f"Phase 4 input not found: {phase4_json}")

    payload = json.loads(phase4_json.read_text(encoding="utf-8"))
    final_response = format_final_response(payload, top_n=top_n).to_dict()

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(final_response, indent=2), encoding="utf-8")
    return final_response


def main() -> None:
    args = parse_args()
    output = run_pipeline(
        phase4_json=Path(args.phase4_json),
        output_json=Path(args.output_json),
        top_n=args.top_n,
    )
    print("Phase 5 pipeline completed.")
    print(f"Status: {output.get('status')}")
    print(f"Recommendations returned: {len(output.get('recommendations', []))}")
    print(f"Output: {args.output_json}")


if __name__ == "__main__":
    main()

