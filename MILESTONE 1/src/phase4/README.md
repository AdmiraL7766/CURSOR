# Phase 4 - LLM Recommendation Layer

Implements the Phase 4 architecture:

- Prompt builder using preferences + Phase 3 candidates
- LLM inference service (Groq by default, OpenAI-compatible API)
- Strict output parser and validator
- Deterministic fallback when remote LLM is not configured or fails

## Run

```bash
python -m src.phase4.pipeline ^
  --phase3-json "data/processed/phase3_candidates.json" ^
  --output-json "data/processed/phase4_recommendations.json" ^
  --top-n 5
```

## Groq Configuration (Recommended)

Set environment variables to enable remote mode with Groq:

- `GROQ_API_KEY` (required)
- `LLM_MODEL` (optional, default `llama-3.3-70b-versatile`)
- `LLM_API_URL` (optional, default `https://api.groq.com/openai/v1/chat/completions`)

`LLM_API_KEY` is also supported and overrides `GROQ_API_KEY` if both are set.

If keys are missing or invalid, the pipeline safely falls back to deterministic ranking.

