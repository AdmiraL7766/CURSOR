# Phase 2 - Preference Capture Layer

This folder implements Phase 2 from `DOCS/phase-wise-architecture.md`.

## Included Components

- Input interface (CLI)
- Input validation and normalization rules
- Standardized preference schema object

## Run

```bash
python -m src.phase2.pipeline \
  --location "Delhi NCR" \
  --budget "800" \
  --cuisine "north indian" \
  --min-rating "4.0" \
  --additional-preference "family-friendly" \
  --additional-preference "quick service"
```

The command prints a validated JSON preference object.

