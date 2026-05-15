# Phase 1 Implementation Plan: Data Foundation

This document defines how to implement **Phase 1: Data Foundation** for the AI-Powered Restaurant Recommendation System.

Reference architecture: `DOCS/phase-wise-architecture.md`

---

## 1) Phase Objective

Build a clean, reliable, and query-ready restaurant data layer by:

- Loading the Zomato dataset from Hugging Face
- Cleaning and normalizing raw records
- Extracting required recommendation features
- Storing validated data in a local database/file format

---

## 2) Scope of Phase 1

### In Scope

- Dataset ingestion from source URL
- Schema validation and data quality checks
- Data cleaning (missing values, type normalization, duplicates)
- Standardized feature table creation
- Persistent storage for downstream phases
- Basic ingestion logs and data quality report

### Out of Scope

- UI development
- LLM prompting and recommendation generation
- Final ranking/business logic for user-facing responses

---

## 3) Inputs and Outputs

### Input

- Source dataset:  
  [https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)

### Output

- Cleaned, validated, query-ready restaurant table with fields:
  - `restaurant_id` (generated or source key)
  - `name`
  - `location`
  - `cuisine`
  - `cost_for_two` (normalized numeric)
  - `rating` (normalized numeric)
  - `is_active` (optional, default true if unknown)
  - `source_updated_at` (if available)
  - `ingested_at`
- Data quality report (counts of dropped/fixed rows)
- Reproducible ingestion script/pipeline

---

## 4) Detailed Task Breakdown

## Task 4.1 - Setup Data Ingestion Module

Create a script/module (for example `src/data/ingest.py`) that:

- Fetches dataset from Hugging Face
- Supports retry with exponential backoff
- Saves raw snapshot for reproducibility (for example `data/raw/zomato_YYYYMMDD.csv`)

**Failure handling:**

- On download failure, retry N times
- If retries fail, use latest raw snapshot if available

## Task 4.2 - Define Canonical Schema

Create schema definition (for example `src/data/schema.py`) that maps source columns to canonical fields.

**Example canonical mapping:**

- source restaurant name -> `name`
- source city/area -> `location`
- source cuisine text -> `cuisine`
- source cost field -> `cost_for_two`
- source rating field -> `rating`

**Validation rules:**

- Required: `name`, `location`, `cuisine`, `cost_for_two`, `rating`
- `rating` range: 0.0 to 5.0
- `cost_for_two` must be positive

## Task 4.3 - Data Cleaning and Normalization

Implement preprocessing (for example `src/data/clean.py`) to:

- Trim whitespace and normalize case where required
- Remove currency symbols and parse numeric cost
- Convert ratings to numeric
- Handle null/invalid values:
  - Drop rows missing required fields
  - Fill optional fields with safe defaults
- Standardize location names (for example alias mapping)
- Standardize cuisine delimiter format

## Task 4.4 - Deduplication

Implement dedupe logic:

- Build dedupe key using normalized `name + location + cuisine`
- Keep highest-quality record when duplicates exist:
  - Prefer row with non-null rating and cost
  - Prefer latest source timestamp if present

## Task 4.5 - Feature Extraction

Prepare downstream-ready feature table (`restaurants_clean`) with only required fields for retrieval/recommendation phases.

Add derived attributes if useful:

- `budget_tier` from `cost_for_two` (low/medium/high)
- `rating_bucket` (for analytics/debug only)

## Task 4.6 - Storage Layer

Choose one initial storage option:

- **Option A (recommended for milestone):** SQLite (`data/processed/restaurants.db`)
- **Option B:** CSV/Parquet (`data/processed/restaurants_clean.parquet`)
- **Option C:** PostgreSQL for multi-user deployment

Store:

- final cleaned table
- ingestion metadata table (`run_id`, row counts, status, timestamp)

## Task 4.7 - Data Quality Report

Generate report (for example `data/reports/phase1_data_quality.md`) including:

- Total rows ingested
- Rows dropped (with reasons)
- Rows fixed/normalized
- Duplicate count removed
- Final usable row count
- Schema validation status

---

## 5) Suggested Folder Structure

```text
project-root/
  src/
    data/
      ingest.py
      schema.py
      clean.py
      dedupe.py
      transform.py
      load.py
  data/
    raw/
    processed/
    reports/
  DOCS/
    phase1.md
```

---

## 6) Definition of Done (DoD)

Phase 1 is complete when all conditions are true:

- [ ] Dataset ingestion runs successfully from source or fallback snapshot
- [ ] Canonical schema is enforced
- [ ] Invalid and duplicate records are handled correctly
- [ ] Cleaned dataset is saved to persistent storage
- [ ] Data quality report is generated for each run
- [ ] Output table can be queried by location, cuisine, budget, and rating
- [ ] Pipeline can be rerun reproducibly without manual edits

---

## 7) Acceptance Criteria

- A test query for a sample city returns valid restaurants with non-null `name`, `location`, `cuisine`, `cost_for_two`, and `rating`.
- At least one ingestion run report is present and documents row-level quality metrics.
- Data layer is stable enough for Phase 2 (Preference Capture) and Phase 3 (Candidate Retrieval).

---

## 8) Risks and Mitigations (Phase 1)

- **Risk:** Source dataset schema changes  
  **Mitigation:** Strict schema check + versioned mapping file

- **Risk:** Poor data quality reduces recommendation quality  
  **Mitigation:** Strong validation, reject logs, quality thresholds

- **Risk:** Pipeline breaks on transient network errors  
  **Mitigation:** Retry strategy + snapshot fallback

---

## 9) Phase 1 Handoff to Phase 2/3

Before starting next phases, publish:

- Final table name/path (single source of truth)
- Column dictionary and data types
- Known limitations (for example sparse locations)
- Last successful ingestion timestamp

This handoff ensures Preference Capture and Candidate Retrieval can integrate without schema confusion.
