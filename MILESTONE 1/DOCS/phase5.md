# Phase 5 Implementation Plan: Response and Presentation Layer

This document defines how to implement **Phase 5: Response and Presentation Layer** for the AI-Powered Restaurant Recommendation System.

Reference architecture: `DOCS/phase-wise-architecture.md`

---

## 1) Phase Objective

Deliver Phase 4 recommendations in a user-friendly, stable response format for frontend/API consumption.

Phase 5 converts raw recommendation output into:

- clean top-N recommendation cards
- consistent API response payload
- explanation-first display content ("why this restaurant fits")

---

## 2) Scope of Phase 5

### In Scope

- Response formatter (JSON + UI-friendly view model)
- Frontend/API contract for top-N suggestions
- Explanation block formatting for each recommendation
- Metadata enrichment for observability of response mode/provider

### Out of Scope

- Recommendation generation logic (Phase 4)
- Monitoring/tuning feedback loop (Phase 6)

---

## 3) Inputs and Outputs

### Inputs

- Phase 4 recommendation payload  
  Example: `data/processed/phase4_recommendations.json`

### Output

Final response payload:

- `status`
- `message`
- `preferences`
- `summary`
- `recommendations` (UI-friendly cards)
- `metadata`

Example output path:

- `data/processed/final_response.json`

---

## 4) Detailed Task Breakdown

## Task 4.1 - Define Presentation Schema

Create structured contracts (for example in `src/phase5/schema.py`):

- `RecommendationCard`
- `FinalResponsePayload`

Required card fields:

- `rank`
- `restaurant_id`
- `title`
- `cuisine`
- `rating`
- `estimated_cost_for_two`
- `explanation`
- `tags`

## Task 4.2 - Build Response Formatter

Create `src/phase5/formatter.py` to:

- transform Phase 4 recommendations into UI-ready cards
- normalize display fields and defaults
- generate tags (for example `top-rated`, `budget-friendly`, `fallback-ranked`)
- cap results to configured `top_n`

## Task 4.3 - Add Summary and Message Logic

Ensure final payload always includes:

- human-readable summary
- explicit status message:
  - `success` when recommendations exist
  - `empty` when no recommendations are available

## Task 4.4 - Add Metadata for Frontend and Debugging

Populate metadata fields:

- `top_n_requested`
- `recommendations_returned`
- `llm_mode`
- `llm_provider`
- `candidate_count_received`

This allows frontend and operators to understand response quality and mode.

## Task 4.5 - Create Pipeline Entrypoint

Create `src/phase5/pipeline.py` with CLI options:

- `--phase4-json`
- `--output-json`
- `--top-n`

Pipeline should load Phase 4 output, format response payload, and save final JSON.

---

## 5) Suggested Folder Structure

```text
project-root/
  src/
    phase5/
      __init__.py
      schema.py
      formatter.py
      pipeline.py
      README.md
  DOCS/
    phase5.md
```

---

## 6) Definition of Done (DoD)

Phase 5 is complete when all conditions are true:

- [ ] Final payload schema is stable and documented
- [ ] Top-N response is correctly capped and ordered
- [ ] Every recommendation includes explanation text
- [ ] Empty-state response is handled gracefully
- [ ] Frontend-facing metadata fields are present

---

## 7) Acceptance Criteria

- Valid Phase 4 input produces final response with `status=success`.
- Empty recommendation list produces valid `status=empty` response.
- Output cards include standardized display keys and explanation text.
- Metadata contains mode/provider/count context.
- Output JSON is directly consumable by API/frontend without additional transforms.

---

## 8) Risks and Mitigations (Phase 5)

- **Risk:** Inconsistent field names break frontend rendering  
  **Mitigation:** enforce strict schema contract in formatter

- **Risk:** Missing explanations reduce user trust  
  **Mitigation:** auto-fill default explanation text when absent

- **Risk:** Overly verbose or unclear payloads  
  **Mitigation:** keep response compact and view-model oriented

---

## 9) Test Cases (Minimum)

- [ ] Standard success response with top-N recommendations
- [ ] Empty recommendation handling
- [ ] Missing optional fields fallback behavior
- [ ] Tag generation correctness for rating/cost/mode
- [ ] Metadata integrity checks
- [ ] JSON contract compatibility with frontend consumer

---

## 10) Phase 5 Handoff to Phase 6

Before starting Phase 6, publish:

- Final response schema and sample payload
- Status/message behavior contract
- Metadata definitions for monitoring integration
- Known display limitations or placeholder rules

This handoff ensures Monitoring and Improvement Layer can instrument real response outcomes reliably.
