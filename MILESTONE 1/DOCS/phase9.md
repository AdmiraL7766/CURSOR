# Phase 9: Deployment Using Streamlit

## Overview
Phase 9 provides an alternative frontend interface using **Streamlit**. While Phase 7 implemented a Next.js application, this phase creates a Python-native, easily deployable dashboard. It can run in two modes:

1. **Standalone mode** (default): Runs the full pipeline (Phases 2–5) directly in-process. No backend server required.
2. **API mode**: Calls the Phase 6 FastAPI backend when the `API_URL` environment variable is set.

## Files
| File | Purpose |
|------|---------|
| `streamlit_app.py` | Main entry point at project root (Streamlit Cloud convention) |
| `src/phase9/app.py` | Lightweight API-only client (alternative, requires backend) |
| `.streamlit/config.toml` | Streamlit theming (Zomato red palette) and server config |

## Core Components
- **Location Selection**: Loads available locations directly from `restaurants_clean.csv` (standalone) or from the `/api/v1/locations` endpoint (API mode).
- **Preference Form**: Sidebar form collecting `location`, `cuisine`, `budget`, `min_rating`, `additional_preferences` (extras), and `top_n`.
- **Recommendation Display**: Renders the AI summary, restaurant cards with rating/cost/cuisine metrics, LLM-generated explanations, and tags.
- **Session State**: Results persist across Streamlit reruns so they don't disappear when the user interacts with the sidebar.

## Setup & Running

### Local Development (Standalone Mode — recommended)

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Ensure Phase 1 data exists** (the CSV must be present):
   ```bash
   python -m src.data.pipeline --project-root .
   ```

3. **Run Streamlit**:
   ```bash
   streamlit run streamlit_app.py
   ```
   Opens automatically at `http://localhost:8501`.

### Local Development (API Mode)
If you prefer to run against the FastAPI backend:

1. Start the backend:
   ```bash
   python -m uvicorn src.phase6.main:app --host 0.0.0.0 --port 8000
   ```

2. Run Streamlit with `API_URL` set:
   ```bash
   set API_URL=http://localhost:8000
   streamlit run streamlit_app.py
   ```

### Streamlit Cloud Deployment
1. Push the repo to GitHub (already done at `https://github.com/AdmiraL7766/CURSOR.git`).
2. Go to [share.streamlit.io](https://share.streamlit.io).
3. Connect your GitHub repo.
4. Set the **Main file path** to: `MILESTONE 1/streamlit_app.py`.
5. Add secrets in the Streamlit Cloud dashboard:
   - `GROQ_API_KEY` (required for LLM recommendations)
6. Deploy!

## Architectural Integration
In standalone mode, `streamlit_app.py` imports and runs Phases 2–5 directly inside the Streamlit process. This eliminates the need for a separate backend server, making the app fully self-contained and trivial to deploy on Streamlit Cloud.

```
User ─► Streamlit UI ─► Phase 2 (validate) ─► Phase 3 (retrieve)
                         ─► Phase 4 (LLM rank) ─► Phase 5 (format) ─► UI
```
