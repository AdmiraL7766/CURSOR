"""LLM inference service with Groq-first and fallback modes."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict

_ENV_LOADED = False


def _load_local_env() -> None:
    """Load .env variables from project locations if not already set."""
    global _ENV_LOADED
    if _ENV_LOADED:
        return

    root = Path(__file__).resolve().parents[2]
    env_paths = [root / ".env", root / "src" / ".env"]

    for env_path in env_paths:
        if not env_path.exists():
            continue
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value

    _ENV_LOADED = True


def call_llm(prompt: str, top_n: int = 5) -> Dict[str, Any]:
    """
    Call Groq (OpenAI-compatible endpoint) by default.

    Recommended env vars:
    - GROQ_API_KEY
    Optional overrides:
    - LLM_API_URL (default: https://api.groq.com/openai/v1/chat/completions)
    - LLM_API_KEY (falls back to GROQ_API_KEY)
    - LLM_MODEL (default: llama-3.3-70b-versatile)
    """
    _load_local_env()

    api_url = os.getenv(
        "LLM_API_URL",
        "https://api.groq.com/openai/v1/chat/completions",
    ).strip()
    api_key = os.getenv("LLM_API_KEY", "").strip() or os.getenv("GROQ_API_KEY", "").strip()
    model = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile").strip()

    if not api_url or not api_key:
        return {"mode": "fallback", "provider": "local", "raw_content": ""}

    payload = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": "Return JSON only. No markdown."},
            {"role": "user", "content": prompt},
        ],
    }

    req = urllib.request.Request(
        api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            body = response.read().decode("utf-8")
        parsed = json.loads(body)
        content = parsed["choices"][0]["message"]["content"]
        provider = f"groq:{model}" if "groq.com" in api_url else model
        return {"mode": "remote", "provider": provider, "raw_content": content}
    except Exception as e:
        print(f"LLM API Error: {e}")
        return {"mode": "fallback", "provider": "local", "raw_content": ""}

