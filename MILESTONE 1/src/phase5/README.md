# Phase 5 - Response and Presentation Layer

Implements the Phase 5 architecture:

- Response formatter (JSON + UI-friendly view model)
- Top-N API/frontend payload generation
- Explanation display block per recommendation

## Run

```bash
python -m src.phase5.pipeline ^
  --phase4-json "data/processed/phase4_recommendations.json" ^
  --output-json "data/processed/final_response.json" ^
  --top-n 5
```

## Output

`final_response.json` includes:

- status and message
- user preferences
- summary
- recommendation cards ready for frontend display
- metadata (`llm_mode`, provider, counts)

