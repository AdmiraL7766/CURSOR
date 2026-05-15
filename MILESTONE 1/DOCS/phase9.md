# Phase 9: Deployment Using Streamlit

## Overview
Phase 9 provides an alternative frontend interface using **Streamlit**. While Phase 7 implemented a Next.js application, this phase demonstrates how rapidly a functional, Python-native dashboard can be spun up using Streamlit. It directly interfaces with the Phase 6 FastAPI backend to fetch location suggestions and retrieve AI-curated restaurant recommendations.

## Core Components
- `src/phase9/app.py`: The main Streamlit script.
- **Location Selection**: Fetches available locations dynamically from the backend `/api/v1/locations` endpoint.
- **Preference Form**: A sidebar form collecting `location`, `cuisine`, `budget`, `min_rating`, `additional_preferences` (extras), and `top_n`.
- **Recommendation Display**: Renders the AI summary, restaurant details, ratings, estimated cost, generated explanations, and tags.

## Setup & Running

1. **Ensure Backend is Running**:
   The Streamlit app calls the FastAPI backend on port 8000. You must start it first:
   ```bash
   python -m uvicorn src.phase6.main:app --host 0.0.0.0 --port 8000
   ```

2. **Install Dependencies**:
   Ensure `streamlit` is installed (it has been added to `requirements.txt`).
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Streamlit App**:
   From the project root:
   ```bash
   python -m streamlit run src/phase9/app.py
   ```
   The application will automatically open in your default browser (usually at `http://localhost:8501`).

## Architectural Integration
The Streamlit app acts purely as a presentation layer (Client). It constructs the `RecommendationRequest` payload and POSTs it to the FastAPI service. The core logic—candidate retrieval, LLM prompt engineering, and ranking—remains seamlessly handled by the backend pipeline.
