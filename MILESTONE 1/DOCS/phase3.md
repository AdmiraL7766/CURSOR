# Phase 3 Implementation Plan: Candidate Retrieval Layer

This document defines how to implement **Phase 3: Candidate Retrieval Layer** for the AI-Powered Restaurant Recommendation System.

Reference architecture: `DOCS/phase-wise-architecture.md`

---

## 1) Phase Objective

Narrow down restaurants to the most relevant candidates before LLM-based recommendation generation.

Phase 3 converts:

- Phase 1 cleaned restaurant data
- Phase 2 validated user preferences

into a filtered, pre-ranked candidate set suitable for Phase 4.

---

## 2) Scope of Phase 3

### In Scope

- Rule-based filtering by location, budget, cuisine, and minimum rating
- Candidate pre-scoring to prioritize relevant options
- Fallback logic for sparse/no-match conditions
- Stable output contract for downstream LLM layer

### Out of Scope

- LLM prompt creation/ranking rationale generation (Phase 4)
- Final UX rendering and response formatting (Phase 5)

---

## 3) Inputs and Outputs

### Inputs

- Cleaned restaurant dataset from Phase 1  
  Example: `data/processed/restaurants_clean.csv`
- Validated preference object from Phase 2  
  Example: `data/processed/phase2_preference.json`

### Output

Candidate retrieval payload (JSON), including:

- `preferences`
- `candidates` (top-K filtered and pre-scored restaurants)
- `fallback_steps_used`
- `total_candidates_before_cap`
- `max_candidates`

Example output path:

- `data/processed/phase3_candidates.json`

---

## 4) Detailed Task Breakdown

## Task 4.1 - Build Retrieval Schema

Define a structured output model (for example in `src/phase3/schema.py`) for candidate retrieval results.

Mandatory fields:

- `preferences`
- `candidates`
- `fallback_steps_used`
- `total_candidates_before_cap`
- `max_candidates`

## Task 4.2 - Implement Base Rule Filters

Create deterministic filters in `src/phase3/retrieval.py`:

- Location match (exact/fuzzy contains depending on data consistency)
- Budget tier match (`low`, `medium`, `high`)
- Cuisine match (contains/normalized string match)
- Minimum rating threshold

## Task 4.3 - Implement Candidate Pre-Scoring

Score candidates before top-K cut:

- Rating relevance score
- Budget proximity score
- Cost efficiency signal (optional)

Use weighted scoring to generate deterministic ordering and reduce prompt token waste in Phase 4.

## Task 4.4 - Add Fallback Strategy

When no candidates are found with strict constraints, apply controlled fallback:

1. Relax rating threshold stepwise
2. Expand budget tier scope
3. Expand to nearby locations (if configured)

Each fallback step must be tracked in `fallback_steps_used`.

## Task 4.5 - Add Pipeline Runner

Create runnable entrypoint (for example `src/phase3/pipeline.py`) that:

- Loads Phase 1 CSV
- Loads Phase 2 preference JSON
- Runs retrieval pipeline
- Saves output JSON

CLI arguments:

- `--restaurants-csv`
- `--preferences-json`
- `--output-json`
- `--max-candidates`

## Task 4.6 - Ensure Backward Compatibility

If `budget_tier` is missing in Phase 1 output, derive it from `cost_for_two`:

- `< 600` -> `low`
- `600 - 1500` -> `medium`
- `> 1500` -> `high`

This keeps Phase 3 stable across evolving Phase 1 schemas.

---

## 5) Suggested Folder Structure

```text
project-root/
  src/
    phase3/
      __init__.py
      schema.py
      retrieval.py
      pipeline.py
      README.md
  DOCS/
    phase3.md
```

---

## 6) Definition of Done (DoD)

Phase 3 is complete when all conditions are true:

- [ ] Retrieval runs successfully using Phase 1 + Phase 2 outputs
- [ ] Base filter logic works for location, budget, cuisine, and rating
- [ ] Candidate pre-scoring and ordering are deterministic
- [ ] Fallback flow is triggered correctly when strict search yields no results
- [ ] Output JSON contract is stable and consumable by Phase 4

---

## 7) Acceptance Criteria

- Valid preferences return non-empty candidate set when matching records exist.
- Strict no-match case triggers fallback steps in expected sequence.
- Candidate count is capped at configured `max_candidates`.
- Output JSON includes required metadata and candidate list.
- Repeated runs with same inputs produce consistent candidate ordering.

---

## 8) Risks and Mitigations (Phase 3)

- **Risk:** Overly strict filters cause frequent empty results  
  **Mitigation:** Controlled fallback sequence and transparent fallback logging

- **Risk:** Very broad filters produce large candidate sets and latency  
  **Mitigation:** Deterministic pre-scoring and top-K cap

- **Risk:** Budget mapping inconsistency between phases  
  **Mitigation:** Single budget-tier derivation rule reused across modules

---

## 9) Test Cases (Minimum)

- [ ] Standard match case (expected candidates > 0)
- [ ] No-match strict case triggers rating relaxation
- [ ] Budget expansion fallback works
- [ ] Nearby location expansion works where mapping exists
- [ ] Candidate pre-score sorting is stable
- [ ] Top-K cap respected
- [ ] Missing input files return clear errors
- [ ] Missing `budget_tier` in restaurants is derived correctly

---

## 10) Phase 3 Handoff to Phase 4

Before starting Phase 4, publish:

- Candidate output JSON schema and sample payload
- Scoring dimensions and fallback behavior documentation
- Max candidate cap and token-budget assumptions for LLM context
- Known retrieval limitations (for example sparse city coverage)

This handoff ensures the LLM Recommendation Layer receives high-quality, bounded, and explainable candidate inputs.
