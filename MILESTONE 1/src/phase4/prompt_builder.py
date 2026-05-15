"""Prompt construction for LLM recommendation calls."""

from __future__ import annotations

import json
from typing import Any, Dict, List


def build_recommendation_prompt(preferences: Dict[str, Any], candidates: List[Dict[str, Any]]) -> str:
    guidance = {
        "task": "Rank restaurants and explain why each recommendation fits the user.",
        "constraints": [
            "Only use restaurants present in the provided candidate list.",
            "Return valid JSON only.",
            "Provide a ranked list with concise and factual explanations.",
            "Do not invent attributes that are not in candidate data.",
        ],
        "output_schema": {
            "recommendations": [
                {
                    "restaurant_id": "string",
                    "name": "string",
                    "cuisine": "string",
                    "rating": "number",
                    "cost_for_two": "number",
                    "rank": "integer",
                    "explanation": "string",
                }
            ],
            "summary": "string",
        },
        "preferences": preferences,
        "candidates": candidates,
    }
    return (
        "You are a restaurant recommendation assistant.\n"
        "Read user preferences and candidate restaurants.\n"
        "Return JSON that follows the schema exactly.\n\n"
        f"{json.dumps(guidance, ensure_ascii=True, indent=2)}"
    )

