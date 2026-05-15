# Phase 6 Implementation Plan: Backend API Service Layer

This document defines how to implement **Phase 6: Backend API Service Layer** for the AI-Powered Restaurant Recommendation System.

Reference architecture: `DOCS/phase-wise-architecture.md`

---

## 1) Phase Objective

Expose the entire recommendation pipeline (Phases 2-5) as a robust, scalable REST API.

Phase 6 converts the standalone scripts and python modules into a highly available backend service that a frontend application or external client can query dynamically.

---

## 2) Scope of Phase 6

### In Scope

- FastAPI web server setup
- `/recommend` POST endpoint to accept user preferences
- Integration of Phase 2 (Validation), Phase 3 (Retrieval), Phase 4 (LLM Engine), and Phase 5 (Formatter)
- Loading the cleaned restaurant dataset (Phase 1 output) into memory for fast querying
- Error handling and standard API responses

### Out of Scope

- Frontend web application (Phase 7)
- Advanced rate-limiting or distributed caching (Future optimization)
- User authentication

---

## 3) Inputs and Outputs

### Inputs

- HTTP POST requests containing user preferences:
  - `location`
  - `budget`
  - `cuisine`
  - `min_rating`
  - `additional_preferences`

### Output

- HTTP Response containing the JSON payload defined in Phase 5:
  - `status`
  - `message`
  - `preferences`
  - `summary`
  - `recommendations`
  - `metadata`

---

## 4) Detailed Task Breakdown

## Task 6.1 - Define API Schemas

Create `src/phase6/schemas.py` to define the request model using Pydantic:

- `RecommendationRequest`: Pydantic model for incoming JSON matching the preference input format.

## Task 6.2 - Build the FastAPI Application

Create `src/phase6/main.py`:

- Initialize the FastAPI app.
- Load the `restaurants_clean.csv` dataframe into memory on startup using lifespan events.
- Expose a `POST /api/v1/recommendations` endpoint.

## Task 6.3 - Integrate the Pipeline

Inside the `/recommendations` endpoint:

- Call `validate_preferences` (Phase 2).
- Call `retrieve_candidates` (Phase 3).
- Call `generate_recommendations` (Phase 4).
- Call `format_final_response` (Phase 5).
- Return the dictionary.

## Task 6.4 - Error Handling

Implement global exception handlers for:

- `ValueError` (usually raised by validation rules) -> returns 400 Bad Request.
- `FileNotFoundError` (if dataset is missing) -> returns 500 Internal Server Error.
- General exceptions -> returns 500 Internal Server Error.

---

## 5) Suggested Folder Structure

```text
project-root/
  src/
    phase6/
      __init__.py
      schemas.py
      main.py
      README.md
  DOCS/
    phase6.md
```

---

## 6) Definition of Done (DoD)

Phase 6 is complete when all conditions are true:

- [ ] FastAPI application can be started using Uvicorn.
- [ ] Dataset loads seamlessly into memory upon application startup.
- [ ] The `/api/v1/recommendations` endpoint correctly processes a valid payload.
- [ ] Invalid inputs are rejected with a helpful 400 error message.
- [ ] The endpoint returns the exact schema expected by Phase 5.

---

## 7) Acceptance Criteria

- A POST request to `/api/v1/recommendations` with valid JSON returns an HTTP 200 status and the top 5 restaurant recommendations.
- A POST request missing required fields (e.g., location) returns an HTTP 422 or 400 status.
- The pipeline execution through the API is reasonably fast (excluding external LLM latency).

---

## 8) Risks and Mitigations (Phase 6)

- **Risk:** High memory usage from loading the full dataset.
  **Mitigation:** The Zomato dataset is lightweight, but pandas allows specific column loading if needed.
- **Risk:** LLM API timeouts causing HTTP request failures.
  **Mitigation:** The LLM service already has a fallback. Ensure the FastAPI endpoint does not block other requests by leveraging async/await where possible, or running the blocking LLM call in a thread pool.

---

## 9) Phase 6 Handoff to Phase 7

Before starting Phase 7 (Frontend Application), publish:

- The API endpoint URL and port (e.g., `http://localhost:8000/api/v1/recommendations`).
- An example `curl` request and response payload.
- The OpenAPI documentation URL (e.g., `http://localhost:8000/docs`).

This handoff ensures the frontend developer has a clear, documented API to consume.
