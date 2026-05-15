# Phase 4 Implementation Plan: LLM Recommendation Layer

This document defines how to implement **Phase 4: LLM Recommendation Layer** for the AI-Powered Restaurant Recommendation System.

Reference architecture: `DOCS/phase-wise-architecture.md`

---

## 1) Phase Objective

Generate explainable and personalized restaurant recommendations from the Phase 3 candidate set.

Phase 4 converts filtered candidates into:

- ranked top-N recommendations
- natural-language explanations
- optional concise recommendation summary

---

## 2) Scope of Phase 4

### In Scope

- Prompt builder that injects user preferences and candidate records
- LLM inference service for ranking + explanation generation
- Output parser and schema enforcement for stable downstream consumption
- Safe fallback recommendation mode when LLM is unavailable

### Out of Scope

- Final UI rendering/presentation decisions (Phase 5)
- Monitoring dashboards and tuning loops (Phase 6)

---

## 3) Inputs and Outputs

### Inputs

- Phase 3 candidate payload  
  Example: `data/processed/phase3_candidates.json`
- User preferences included in Phase 3 payload

### Output

Recommendation JSON payload:

- `preferences`
- `recommendations` (ranked list with explanations)
- `summary`
- `llm_mode` (`remote` or `fallback`)
- `llm_provider`
- `candidate_count`

Example output path:

- `data/processed/phase4_recommendations.json`

---

## 4) Detailed Task Breakdown

## Task 4.1 - Define Recommendation Schema

Create structured contracts (for example in `src/phase4/schema.py`):

- `RecommendationItem`
- `RecommendationResult`

Required recommendation item fields:

- `restaurant_id`
- `name`
- `cuisine`
- `rating`
- `cost_for_two`
- `rank`
- `explanation`

## Task 4.2 - Implement Prompt Builder

Create a prompt module (for example `src/phase4/prompt_builder.py`) that:

- Injects preferences and candidate data
- Enforces "use only provided candidates" instruction
- Specifies strict JSON output schema
- Prevents free-form, non-parseable responses

## Task 4.3 - Implement LLM Inference Service

Create `src/phase4/llm_service.py` with:

- Groq-first API call support via environment variables:
  - `GROQ_API_KEY` (recommended)
  - `LLM_API_URL` (optional override, defaults to Groq chat completions endpoint)
  - `LLM_API_KEY` (optional override)
  - `LLM_MODEL` (optional, Groq-supported model)
- Timeout and error handling
- Graceful fallback mode if remote call fails

## Task 4.4 - Implement Output Parser and Validator

Create `src/phase4/parser.py` to:

- Parse returned JSON safely
- Validate required keys and data types
- Reject hallucinated restaurant IDs not present in candidate set
- Repair missing explanation values with default explanation template

## Task 4.5 - Build Recommendation Engine

Create orchestrator (for example `src/phase4/engine.py`) to:

1. Build prompt
2. Call LLM service
3. Parse and validate output
4. If invalid/unavailable, switch to deterministic fallback ranking
5. Return final structured `RecommendationResult`

## Task 4.6 - Pipeline Entrypoint

Create runnable module (`src/phase4/pipeline.py`) with CLI options:

- `--phase3-json`
- `--output-json`
- `--top-n`

The pipeline should read Phase 3 candidates, produce Phase 4 output, and print execution mode summary.

---

## 5) Suggested Folder Structure

```text
project-root/
  src/
    phase4/
      __init__.py
      schema.py
      prompt_builder.py
      llm_service.py
      parser.py
      engine.py
      pipeline.py
      README.md
  DOCS/
    phase4.md
```

---

## 6) Definition of Done (DoD)

Phase 4 is complete when all conditions are true:

- [ ] Prompt includes preferences + candidate set and output schema instruction
- [ ] LLM service supports configured remote inference
- [ ] Parser enforces stable output and rejects invalid candidate references
- [ ] Fallback recommendations are generated when LLM fails
- [ ] Output JSON is consistently consumable by Phase 5

---

## 7) Acceptance Criteria

- Remote mode returns valid ranked recommendations when LLM configuration is present.
- Fallback mode returns valid recommendations when LLM config is absent/fails.
- Every recommendation includes a clear explanation.
- No recommendation references restaurants outside candidate list.
- Repeated runs with same fallback inputs are deterministic.

---

## 8) Risks and Mitigations (Phase 4)

- **Risk:** LLM returns invalid JSON or non-structured text  
  **Mitigation:** strict parser, schema validation, and fallback mode

- **Risk:** Hallucinated recommendations not present in candidates  
  **Mitigation:** candidate ID whitelist validation before acceptance

- **Risk:** Provider/API outages increase response failures  
  **Mitigation:** timeout + graceful deterministic fallback

---

## 9) Test Cases (Minimum)

- [ ] Valid remote LLM call returns parseable JSON
- [ ] Invalid JSON response triggers fallback
- [ ] Hallucinated `restaurant_id` entries are rejected
- [ ] Missing explanations are auto-filled with defaults
- [ ] Top-N enforcement works
- [ ] Output schema remains stable across remote/fallback modes

---

## 10) Phase 4 Handoff to Phase 5

Before starting Phase 5, publish:

- Final recommendation output schema
- Remote vs fallback behavior contract
- Explanation style guidelines
- Sample output payload for UI/API integration

This handoff ensures Response and Presentation Layer can render recommendations consistently without interpretation ambiguity.
