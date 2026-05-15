# Phase 6: Backend API Service Layer

This module exposes the restaurant recommendation pipeline as a RESTful API using FastAPI.

## Overview

The API accepts user preferences (Location, Budget, Cuisine, Rating), validates them using Phase 2, queries the dataset loaded in memory (Phase 3), generates AI recommendations (Phase 4), and formats the final response payload (Phase 5).

## Setup & Running

1. Install requirements:
   ```bash
   pip install fastapi uvicorn
   ```

2. Run the server from the root of the project:
   ```bash
   python -m src.phase6.main
   ```
   Or using Uvicorn directly:
   ```bash
   uvicorn src.phase6.main:app --reload
   ```

## Endpoints

### `POST /api/v1/recommendations`

**Request Body Example:**
```json
{
  "location": "Bellandur",
  "budget": "2000",
  "cuisine": "Any",
  "min_rating": "4.0",
  "additional_preferences": [],
  "top_n": 5
}
```

**Response Format:**
The API returns the exact UI-friendly JSON payload produced by Phase 5, including `status`, `summary`, and the ranked `recommendations` array.

## OpenAPI Documentation

When the server is running, you can explore the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
