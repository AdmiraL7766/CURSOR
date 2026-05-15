# Phase 3 - Candidate Retrieval Layer

Implements the Phase 3 architecture:

- Rule-based filtering using location, budget, cuisine, and minimum rating
- Candidate pre-scoring and top-K selection
- Fallback strategy for sparse/no matches

## Run

```bash
python -m src.phase3.pipeline ^
  --restaurants-csv "data/processed/restaurants_clean.csv" ^
  --preferences-json "data/processed/phase2_preference.json" ^
  --output-json "data/processed/phase3_candidates.json" ^
  --max-candidates 30
```

## Output

`phase3_candidates.json` contains:

- normalized input preferences
- candidate list (filtered and scored)
- fallback steps used (if any)
- total candidate count before top-K cap

