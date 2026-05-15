"""Phase 4 pipeline entrypoint."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from .engine import generate_recommendations


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Phase 4 LLM recommendation layer.")
    parser.add_argument(
        "--phase3-json",
        default="data/processed/phase3_candidates.json",
        help="Input JSON from Phase 3 candidate retrieval.",
    )
    parser.add_argument(
        "--output-json",
        default="data/processed/phase4_recommendations.json",
        help="Output path for ranked recommendations JSON.",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=5,
        help="Number of recommendations to return.",
    )
    return parser.parse_args()


def run_pipeline(phase3_json: Path, output_json: Path, top_n: int = 5) -> Dict[str, Any]:
    if not phase3_json.exists():
        raise FileNotFoundError(f"Phase 3 input not found: {phase3_json}")

    payload = json.loads(phase3_json.read_text(encoding="utf-8"))
    preferences = payload.get("preferences", {})
    candidates = payload.get("candidates", [])
    if not isinstance(candidates, list):
        raise ValueError("Invalid Phase 3 payload. 'candidates' must be a list.")

    result = generate_recommendations(
        preferences=preferences,
        candidates=candidates,
        top_n=top_n,
    )
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
    return result.to_dict()


def main() -> None:
    args = parse_args()
    output = run_pipeline(
        phase3_json=Path(args.phase3_json),
        output_json=Path(args.output_json),
        top_n=args.top_n,
    )
    print("Phase 4 pipeline completed.")
    print(f"Recommendations returned: {len(output.get('recommendations', []))}")
    print(f"Mode: {output.get('llm_mode')} ({output.get('llm_provider')})")
    print(f"Output: {args.output_json}")


if __name__ == "__main__":
    main()

