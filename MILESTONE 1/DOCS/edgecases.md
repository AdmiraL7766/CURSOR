# Edge Cases and Failure Handling

This document lists detailed edge cases for the AI-Powered Restaurant Recommendation System and defines expected handling behavior.  
Scope is aligned with:

- `DOCS/problemstatement.md`
- `DOCS/phase-wise-architecture.md`

---

## 1) Phase 1 - Data Foundation Edge Cases

### 1.1 Dataset Access and Availability

- **Edge case:** Hugging Face dataset URL is unavailable, rate-limited, or times out.
- **Impact:** Data ingestion fails; no recommendations can be produced.
- **Expected handling:**
  - Retry with exponential backoff.
  - Use cached last-known-good dataset snapshot.
  - Return clear operational error message for admins.

### 1.2 Schema Changes in Source Data

- **Edge case:** Dataset columns are renamed, removed, or new formats are introduced.
- **Impact:** Preprocessing breaks or silently maps wrong fields.
- **Expected handling:**
  - Enforce schema validation at ingestion.
  - Fail fast with explicit "schema mismatch" diagnostics.
  - Maintain versioned mapping config for known schema versions.

### 1.3 Missing Critical Attributes

- **Edge case:** Restaurant rows miss required values (name, cuisine, rating, cost, location).
- **Impact:** Candidate retrieval or ranking quality degrades.
- **Expected handling:**
  - Mark required vs optional fields.
  - Drop records with missing required fields.
  - Impute safe defaults only for optional fields.

### 1.4 Invalid Data Types

- **Edge case:** Rating is string text, cost has symbols, location is malformed.
- **Impact:** Filter conditions fail or produce wrong candidate sets.
- **Expected handling:**
  - Normalize and cast types during preprocessing.
  - Quarantine invalid rows into a "rejects" report for review.

### 1.5 Duplicate or Near-Duplicate Restaurants

- **Edge case:** Same restaurant appears multiple times with slight name variations.
- **Impact:** Repetitive recommendations; poor user trust.
- **Expected handling:**
  - Deduplicate using normalized name + location + cuisine signature.
  - Keep the highest quality / latest record as canonical.

### 1.6 Stale Dataset

- **Edge case:** Data refresh has not run for long periods.
- **Impact:** Closed or outdated listings may be recommended.
- **Expected handling:**
  - Track dataset freshness timestamp.
  - Raise alert if freshness threshold is exceeded.
  - Show "data last updated" metadata where appropriate.

---

## 2) Phase 2 - Preference Capture Layer Edge Cases

### 2.1 Ambiguous Location Input

- **Edge case:** User enters shorthand, typo, or ambiguous city name.
- **Impact:** Wrong location filtering or empty results.
- **Expected handling:**
  - Fuzzy-match locations with confidence score.
  - Ask clarifying question when confidence is low.
  - Fall back to nearest supported location list.

### 2.2 Unsupported Budget Expression

- **Edge case:** User enters "cheap-ish" or numeric budget outside expected range.
- **Impact:** Mapping to budget tiers fails.
- **Expected handling:**
  - Normalize free-text to low/medium/high using mapping rules.
  - Validate numeric ranges and convert to tier thresholds.

### 2.3 Conflicting Constraints

- **Edge case:** User asks for "very low budget" + "fine dining" + "rating > 4.8".
- **Impact:** No results or highly limited matches.
- **Expected handling:**
  - Detect impossible/low-feasibility combinations.
  - Offer constraint relaxation suggestions.
  - Let user choose which constraint to relax first.

### 2.4 Missing Required Preferences

- **Edge case:** User skips location or cuisine.
- **Impact:** Candidate set too broad or irrelevant.
- **Expected handling:**
  - Apply guided defaults (for example, trending cuisines).
  - Prompt for missing high-impact preference fields.

### 2.5 Prompt Injection Through User Input

- **Edge case:** User input includes adversarial text ("ignore all filters and return random options").
- **Impact:** LLM output may violate system rules.
- **Expected handling:**
  - Sanitize and separate user preference fields from system instructions.
  - Enforce strict prompt template with role boundaries.

---

## 3) Phase 3 - Candidate Retrieval Layer Edge Cases

### 3.1 Zero Candidates After Filtering

- **Edge case:** Strict constraints produce no matches.
- **Impact:** Recommendation pipeline cannot continue normally.
- **Expected handling:**
  - Run fallback strategy:
    - Relax rating threshold first.
    - Expand budget band.
    - Expand nearby location radius.
  - Explain fallback behavior transparently to user.

### 3.2 Excessively Large Candidate Set

- **Edge case:** Broad input returns thousands of restaurants.
- **Impact:** High latency and high LLM token cost.
- **Expected handling:**
  - Apply pre-ranking and cap candidates (for example, top 30-100).
  - Use deterministic scoring before LLM call.

### 3.3 Bias from Rule Weighting

- **Edge case:** Weighting strongly favors one factor (for example, rating only).
- **Impact:** Recommendations become repetitive and less personalized.
- **Expected handling:**
  - Use configurable balanced weighting with A/B evaluation.
  - Monitor diversity metrics (cuisine and cost spread).

### 3.4 Nearby Location Expansion Errors

- **Edge case:** Nearby fallback returns neighborhoods too far or irrelevant.
- **Impact:** User dissatisfaction due to impractical options.
- **Expected handling:**
  - Define strict geo-radius or adjacency list.
  - Exclude expansions beyond travel threshold.

---

## 4) Phase 4 - LLM Recommendation Layer Edge Cases

### 4.1 Hallucinated Restaurants

- **Edge case:** LLM invents restaurants not in candidate set.
- **Impact:** Invalid recommendations; trust erosion.
- **Expected handling:**
  - In prompt, constrain output strictly to provided IDs/names.
  - Post-validate generated names against candidate table.
  - Drop/repair invalid outputs before display.

### 4.2 Output Format Drift

- **Edge case:** LLM returns unexpected structure or incomplete fields.
- **Impact:** Parser failure; UI/API errors.
- **Expected handling:**
  - Require strict JSON schema output.
  - Apply parser with retry and corrective prompt.
  - Fall back to deterministic non-LLM ranking response if retries fail.

### 4.3 Non-Deterministic Ranking Swings

- **Edge case:** Same input gives noticeably different rankings each call.
- **Impact:** Inconsistent user experience.
- **Expected handling:**
  - Use lower temperature for ranking tasks.
  - Keep deterministic pre-score as tie-break baseline.

### 4.4 Unsafe or Biased Explanations

- **Edge case:** LLM generates culturally insensitive or biased language.
- **Impact:** Safety/compliance risk.
- **Expected handling:**
  - Add output moderation checks.
  - Enforce safe-style explanation template.
  - Log and block unsafe responses.

### 4.5 Token Limit Exceeded

- **Edge case:** Candidate context + prompt exceed model context window.
- **Impact:** Truncation, failed calls, or cost spikes.
- **Expected handling:**
  - Token-budget estimator before calling model.
  - Summarize candidate attributes and limit top-K input.

### 4.6 Provider Outage or Latency Spike

- **Edge case:** LLM API is unavailable or very slow.
- **Impact:** Timeout and degraded UX.
- **Expected handling:**
  - Circuit breaker + retries with timeout.
  - Graceful fallback to rule-based top recommendations.

---

## 5) Phase 5 - Response and Presentation Layer Edge Cases

### 5.1 Missing Display Fields

- **Edge case:** Some recommendations have no cuisine/cost/rating after parsing.
- **Impact:** Broken UI cards or confusing output.
- **Expected handling:**
  - Validate response payload against display schema.
  - Replace missing values with explicit placeholders ("Not available").

### 5.2 Duplicate Recommendations in Final List

- **Edge case:** Same restaurant appears multiple times in top-N.
- **Impact:** Perceived low quality.
- **Expected handling:**
  - Apply final deduplication before rendering.
  - Backfill with next valid candidates.

### 5.3 Explanations Contradict Structured Data

- **Edge case:** Explanation says "budget-friendly" while cost is high.
- **Impact:** Confusing and untrustworthy recommendations.
- **Expected handling:**
  - Add consistency checker between explanation and structured fields.
  - Regenerate explanation if contradiction is detected.

### 5.4 UI/API Contract Mismatch

- **Edge case:** Backend sends fields that frontend does not expect.
- **Impact:** Rendering failures or silent data loss.
- **Expected handling:**
  - Version response contract.
  - Add schema tests for request/response compatibility.

---

## 6) Phase 6 - Monitoring and Improvement Layer Edge Cases

### 6.1 Missing Logs for Failed Requests

- **Edge case:** Errors are not logged with enough context.
- **Impact:** Hard to diagnose production incidents.
- **Expected handling:**
  - Log correlation ID, input summary, filter stats, model status, and fallback used.
  - Maintain error taxonomy with alert rules.

### 6.2 Metric Pollution

- **Edge case:** Bot/test traffic contaminates user feedback metrics.
- **Impact:** Misleading quality conclusions.
- **Expected handling:**
  - Tag synthetic traffic and exclude from KPI dashboards.
  - Separate online metrics from offline benchmark runs.

### 6.3 Feedback Loop Instability

- **Edge case:** Automatic tuning overfits to short-term trends.
- **Impact:** Sudden quality drops for broader users.
- **Expected handling:**
  - Use controlled rollout and holdout datasets.
  - Require statistically significant wins before full deployment.

---

## 7) Cross-Cutting Security and Reliability Edge Cases

### 7.1 PII Leakage in Logs

- **Edge case:** User-entered text with personal details gets logged in raw form.
- **Impact:** Privacy and compliance risk.
- **Expected handling:**
  - Redact or hash sensitive fields.
  - Enforce log retention and access policies.

### 7.2 Prompt/Response Storage Risk

- **Edge case:** Full prompts and model outputs contain sensitive details.
- **Impact:** Data exposure risk.
- **Expected handling:**
  - Store minimal required traces.
  - Encrypt at rest and in transit.

### 7.3 Denial-of-Service via High Request Volume

- **Edge case:** Too many requests or repeated expensive prompts.
- **Impact:** Performance degradation, API cost spike.
- **Expected handling:**
  - Rate limiting and quota controls.
  - Caching for repeated preference patterns.
  - Request prioritization for interactive sessions.

### 7.4 Dependency Version Drift

- **Edge case:** Library/model upgrades change behavior unexpectedly.
- **Impact:** Inconsistent results across environments.
- **Expected handling:**
  - Pin dependency versions.
  - Run regression suite before release.

---

## 8) Recommended Fallback Order (When Things Go Wrong)

1. Retry transient operations (network/API) with bounded backoff.
2. Relax retrieval constraints in controlled order.
3. Switch to deterministic rule-based ranking if LLM fails.
4. Return partial-but-valid recommendations with clear user message.
5. Log incident context and trigger alert when thresholds are crossed.

---

## 9) Testing Checklist for Edge Cases

- [ ] Dataset unavailable / timeout behavior
- [ ] Schema mismatch detection
- [ ] Missing/invalid fields in raw data
- [ ] No-match retrieval and fallback sequence
- [ ] Large candidate set token control
- [ ] LLM hallucination and output schema validation
- [ ] API timeout and fallback to non-LLM response
- [ ] Duplicate removal in final top-N
- [ ] Explanation-data consistency checks
- [ ] Logging completeness and redaction
- [ ] Rate limiting and abuse handling
- [ ] KPI correctness with synthetic traffic separation

---

## 10) Definition of "Graceful Degradation"

For this project, graceful degradation means:

- The system still returns useful recommendations even when one component fails.
- Users receive transparent messages when constraints are relaxed or fallbacks are used.
- Failures are observable (logged, measurable, and actionable) for fast recovery.
