# Phase 2 Implementation Plan: Preference Capture Layer

This document defines how to implement **Phase 2: Preference Capture Layer** for the AI-Powered Restaurant Recommendation System.

Reference architecture: `DOCS/phase-wise-architecture.md`

---

## 1) Phase Objective

Collect, validate, and standardize user preferences before candidate retrieval and recommendation generation.

Phase 2 converts raw user inputs into a structured preference object that can be consumed directly by Phase 3 (Candidate Retrieval).

---

## 2) Scope of Phase 2

### In Scope

- Input interface for capturing user preferences (CLI/Web/API compatible)
- Validation rules for location, budget, cuisine, and minimum rating
- Normalization and standardization of raw input values
- Standard preference schema/model output
- Clear error messages for invalid input

### Out of Scope

- Candidate filtering and ranking logic (Phase 3)
- LLM recommendation generation (Phase 4)
- UI design details beyond preference input contracts

---

## 3) Inputs and Outputs

### Input

User-provided preference fields:

- `location` (for example, Delhi, Bangalore)
- `budget` (low, medium, high, alias text, or numeric)
- `cuisine` (for example, Italian, Chinese, North Indian)
- `min_rating` (0.0 to 5.0)
- `additional_preferences` (optional list such as family-friendly, quick service)

### Output

A structured and validated preference object:

- `location` (normalized)
- `budget_tier` (`low` | `medium` | `high`)
- `cuisine` (normalized)
- `min_rating` (float in valid range)
- `additional_preferences` (cleaned and deduplicated list)
- `original_budget_input` (for traceability)

---

## 4) Detailed Task Breakdown

## Task 4.1 - Define Preference Schema

Create a schema/model (for example `src/phase2/schema.py`) with strict fields and types.

**Required fields:**

- `location`
- `budget_tier`
- `cuisine`
- `min_rating`

**Optional fields:**

- `additional_preferences`
- `original_budget_input`

## Task 4.2 - Build Input Interface

Implement at least one ingestion interface:

- **CLI** for milestone delivery (required)
- Optional extension: Web form/API endpoint

CLI should accept:

- `--location`
- `--budget`
- `--cuisine`
- `--min-rating`
- repeated `--additional-preference`

## Task 4.3 - Implement Validation Rules

Enforce strong validation before output generation:

- **Location:** required, trimmed, alias normalization
- **Budget:** support tier names, alias values, and numeric conversion
- **Cuisine:** required and normalized
- **Min rating:** numeric and within `[0, 5]`
- **Additional preferences:** optional, non-empty unique normalized strings

Return precise, actionable validation errors when checks fail.

## Task 4.4 - Implement Normalization

Normalize user input into canonical values:

- Location alias mapping (for example `blr -> Bangalore`)
- Budget alias/numeric mapping:
  - low: small budget range
  - medium: moderate budget range
  - high: premium budget range
- Cuisine casing and whitespace normalization
- Deduplication for additional preferences

## Task 4.5 - Standardized Output Contract

Emit a stable preference object:

- JSON print to stdout (CLI mode)
- Optional JSON write to output path
- Contract must remain backward compatible for Phase 3 integration

## Task 4.6 - Error Handling and UX Messages

Handle edge conditions cleanly:

- Missing required fields
- Invalid rating format or out-of-range rating
- Unsupported budget text
- Empty strings after trimming

Each error should tell user:

- which field failed
- why it failed
- accepted input format

---

## 5) Suggested Folder Structure

```text
project-root/
  src/
    phase2/
      __init__.py
      schema.py
      validators.py
      interface.py
      pipeline.py
      README.md
  DOCS/
    phase2.md
```

---

## 6) Definition of Done (DoD)

Phase 2 is complete when all conditions are true:

- [ ] Input interface accepts all required preference fields
- [ ] Validation blocks invalid inputs with clear messages
- [ ] Normalization rules produce canonical values
- [ ] Output follows standardized preference schema
- [ ] CLI prints valid JSON object for successful input
- [ ] Preference object is directly consumable by Phase 3

---

## 7) Acceptance Criteria

- A valid sample input produces a normalized structured preference object.
- Invalid rating (for example `6.1`) is rejected with informative error.
- Numeric budget input maps correctly to budget tiers.
- Duplicate additional preferences are removed while preserving order.
- Output contract remains stable across repeated runs.

---

## 8) Risks and Mitigations (Phase 2)

- **Risk:** Ambiguous location names reduce match quality  
  **Mitigation:** Alias mapping + optional clarification prompts

- **Risk:** Free-text budget is inconsistent  
  **Mitigation:** Alias dictionary + numeric threshold mapping

- **Risk:** Overly strict validation hurts usability  
  **Mitigation:** Human-friendly error messages and safe defaults where possible

---

## 9) Test Cases (Minimum)

- [ ] Valid standard input (`Delhi`, `medium`, `Italian`, `4.0`)
- [ ] Valid alias budget (`affordable` -> `low`)
- [ ] Valid numeric budget (`1200` -> `medium`)
- [ ] Invalid budget text (`ultra cheap++`)
- [ ] Invalid rating text (`good`)
- [ ] Invalid rating range (`-1`, `5.9`)
- [ ] Empty cuisine/location handling
- [ ] Multiple additional preferences with duplicates

---

## 10) Phase 2 Handoff to Phase 3

Before starting Phase 3, publish:

- Final preference schema fields and types
- Validation/normalization rules applied per field
- Error response format for invalid input
- Sample valid preference JSON payload

This handoff ensures Candidate Retrieval can filter data consistently without input ambiguity.
