"""
Streamlit App — Zomato AI Restaurant Recommendations (Phase 9).

This is the main entry point for Streamlit Cloud deployment.
It can operate in two modes:
  1. **Standalone** (default): Runs the full recommendation pipeline directly
     (Phases 2–5) without requiring the FastAPI backend.
  2. **API mode**: Calls the Phase 6 FastAPI backend if the environment variable
     API_URL is set.
"""

import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Ensure the project root is on sys.path so `src.*` imports resolve correctly.
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Page config — must be the first Streamlit call.
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Zomato AI — Restaurant Recommendations",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CSV_PATH = PROJECT_ROOT / "data" / "processed" / "restaurants_clean.csv"
API_URL = os.getenv("API_URL", "")  # empty = standalone mode

CUISINES = [
    "Any",
    "North Indian",
    "South Indian",
    "Chinese",
    "Italian",
    "Continental",
    "Mughlai",
    "Fast Food",
    "Cafe",
    "Biryani",
    "Street Food",
]

BUDGET_LABELS = {
    "low": "₹ Pocket Friendly",
    "medium": "₹₹ Mid Range",
    "high": "₹₹₹ Luxury",
}

RATING_OPTIONS = {
    "0": "Any rating",
    "3.0": "3.0+",
    "3.5": "3.5+",
    "4.0": "4.0+",
    "4.5": "4.5+",
}


# ---------------------------------------------------------------------------
# Data loading (cached so we don't re-read on every interaction)
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="Loading restaurant data…")
def load_restaurants() -> pd.DataFrame:
    """Load and return the processed restaurant dataset."""
    if not CSV_PATH.exists():
        st.error(
            f"Dataset not found at `{CSV_PATH}`. "
            "Please run Phase 1 first: `python -m src.data.pipeline --project-root .`"
        )
        st.stop()

    df = pd.read_csv(CSV_PATH)

    # Ensure budget_tier exists (backward compatibility)
    if "budget_tier" not in df.columns:
        costs = pd.to_numeric(df["cost_for_two"], errors="coerce").fillna(0)
        df["budget_tier"] = costs.apply(
            lambda c: "low" if c < 600 else ("medium" if c <= 1500 else "high")
        )

    return df


@st.cache_data(show_spinner=False)
def get_locations(df: pd.DataFrame):
    """Extract unique, sorted location list from the dataset."""
    locs = df["location"].astype(str).str.strip().unique().tolist()
    return sorted([l for l in locs if l and l != "nan"])


# ---------------------------------------------------------------------------
# Pipeline execution (standalone mode — no backend needed)
# ---------------------------------------------------------------------------
def run_pipeline(df, location, budget, cuisine, min_rating, extras, top_n):
    """Execute Phases 2–5 in-process and return the final response dict."""
    from src.phase2.validators import validate_preferences
    from src.phase3.retrieval import RetrievalConfig, retrieve_candidates
    from src.phase4.engine import generate_recommendations
    from src.phase5.formatter import format_final_response

    # Phase 2 — Preference validation
    pref = validate_preferences(
        location=location,
        budget=budget,
        cuisine=cuisine,
        min_rating=min_rating,
        additional_preferences=extras,
    )
    pref_dict = pref.to_dict()

    # Phase 3 — Candidate retrieval
    config = RetrievalConfig(max_candidates=30)
    retrieval = retrieve_candidates(
        restaurants=df, preferences=pref_dict, config=config
    ).to_dict()

    candidates = retrieval.get("candidates", [])

    # Phase 4 — LLM recommendation
    rec_result = generate_recommendations(
        preferences=pref_dict,
        candidates=candidates,
        top_n=top_n,
    )

    # Phase 5 — Final formatting
    final = format_final_response(rec_result.to_dict(), top_n=top_n).to_dict()
    return final


# ---------------------------------------------------------------------------
# API mode helpers
# ---------------------------------------------------------------------------
def run_via_api(location, budget, cuisine, min_rating, extras, top_n):
    """Call the Phase 6 FastAPI backend and return the JSON response."""
    import requests

    payload = {
        "location": location,
        "cuisine": cuisine,
        "budget": budget,
        "min_rating": min_rating,
        "top_n": top_n,
        "additional_preferences": extras,
    }
    resp = requests.post(
        f"{API_URL}/api/v1/recommendations", json=payload, timeout=60
    )
    resp.raise_for_status()
    return resp.json()


# ===================================================================
#                           UI LAYOUT
# ===================================================================
def main():
    df = load_restaurants()
    locations = get_locations(df)

    # ------------------------------------------------------------------
    # Custom CSS — Zomato-inspired palette
    # ------------------------------------------------------------------
    st.markdown(
        """
        <style>
        /* Zomato red accent */
        :root {
            --zomato-red: #E23744;
            --zomato-dark: #1C1C1C;
        }
        .stApp {
            background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
        }
        h1, h2, h3 { color: var(--zomato-dark); }
        .stButton > button[kind="primary"] {
            background-color: var(--zomato-red) !important;
            border: none;
        }
        .restaurant-card {
            background: #fff;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 16px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
            border-left: 4px solid var(--zomato-red);
        }
        .tag-badge {
            display: inline-block;
            background: #f0f2f6;
            color: #444;
            font-size: 13px;
            padding: 3px 10px;
            border-radius: 14px;
            margin-right: 6px;
            margin-top: 4px;
        }
        .metric-row { display: flex; gap: 32px; margin: 8px 0 12px 0; }
        .metric-item { font-size: 15px; }
        .metric-label { font-weight: 600; color: #888; font-size: 12px; text-transform: uppercase; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ------------------------------------------------------------------
    # Header
    # ------------------------------------------------------------------
    st.markdown(
        "<h1 style='text-align:center; margin-bottom:0;'>🍽️ Zomato AI Recommendations</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center; color:#888; margin-top:0;'>"
        "Personalized AI recommendations based on your mood and budget</p>",
        unsafe_allow_html=True,
    )

    # ------------------------------------------------------------------
    # Sidebar — Preferences
    # ------------------------------------------------------------------
    with st.sidebar:
        st.header("🔍 Your Preferences")
        st.caption("Customize your restaurant search below.")

        selected_location = st.selectbox(
            "📍 Location",
            options=[""] + locations,
            format_func=lambda x: "Select a location…" if x == "" else x,
            help="Pick a neighborhood in Bangalore",
        )
        if not selected_location:
            selected_location = st.text_input(
                "Or type a location", placeholder="e.g. Bellandur"
            )

        cuisine = st.selectbox("🍳 Cuisine", CUISINES)

        budget = st.selectbox(
            "💰 Budget",
            options=list(BUDGET_LABELS.keys()),
            format_func=lambda k: BUDGET_LABELS[k],
        )

        min_rating = st.selectbox(
            "⭐ Minimum Rating",
            options=list(RATING_OPTIONS.keys()),
            format_func=lambda k: RATING_OPTIONS[k],
            index=2,  # default to 3.5+
        )

        extras_raw = st.text_input(
            "🏷️ Extras (comma-separated)",
            placeholder="e.g. romantic, live music, outdoor",
        )

        st.divider()
        top_n = st.slider("Number of recommendations", 1, 10, 5)

        search = st.button("🔎  Search", type="primary", use_container_width=True)

    # ------------------------------------------------------------------
    # Main content area
    # ------------------------------------------------------------------
    if search:
        if not selected_location:
            st.warning("⚠️ Please select or type a location first.")
            return

        extras = [p.strip() for p in extras_raw.split(",") if p.strip()]

        with st.spinner("✨ Curating your perfect picks…"):
            try:
                if API_URL:
                    result = run_via_api(
                        selected_location, budget, cuisine, min_rating, extras, top_n
                    )
                else:
                    result = run_pipeline(
                        df, selected_location, budget, cuisine, min_rating, extras, top_n
                    )
            except Exception as exc:
                st.error(f"Something went wrong: {exc}")
                return

        # Store results in session state so they persist across reruns
        st.session_state["result"] = result

    # ------------------------------------------------------------------
    # Render results (from session state so they survive reruns)
    # ------------------------------------------------------------------
    result = st.session_state.get("result")

    if result:
        st.divider()

        # AI Summary
        summary = result.get("summary", "")
        if summary:
            st.info(f"✨ **AI Summary:** {summary}")

        recommendations = result.get("recommendations", [])

        if not recommendations:
            st.warning(
                "No restaurants matched your preferences. "
                "Try broadening your filters or changing the location."
            )
        else:
            st.subheader(f"🏆 Top {len(recommendations)} Recommendations")

            for rec in recommendations:
                rank = rec.get("rank", "")
                title = rec.get("title", "Unknown")
                cuisine_val = rec.get("cuisine", "")
                rating = rec.get("rating", 0)
                cost = rec.get("estimated_cost_for_two", 0)
                explanation = rec.get("explanation", "")
                tags = rec.get("tags", [])

                st.markdown(
                    f"""
                    <div class="restaurant-card">
                        <h3 style="margin:0 0 4px 0;">#{rank} {title}</h3>
                        <div class="metric-row">
                            <div class="metric-item"><span class="metric-label">Rating</span><br>⭐ {rating}</div>
                            <div class="metric-item"><span class="metric-label">Cost for Two</span><br>₹{cost:,.0f}</div>
                            <div class="metric-item"><span class="metric-label">Cuisine</span><br>{cuisine_val}</div>
                        </div>
                        <p style="color:#555; margin:8px 0;"><b>Why we recommend it:</b> {explanation}</p>
                        <div>{''.join(f'<span class="tag-badge">{t}</span>' for t in tags)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Metadata footer
            meta = result.get("metadata", {})
            if meta:
                with st.expander("📊 Response Metadata"):
                    col1, col2, col3 = st.columns(3)
                    col1.metric("LLM Mode", meta.get("llm_mode", "N/A"))
                    col2.metric("Candidates", meta.get("candidate_count_received", 0))
                    col3.metric("Returned", meta.get("recommendations_returned", 0))
    else:
        # Empty / initial state
        st.markdown(
            "<div style='text-align:center; padding:80px 20px; color:#bbb;'>"
            "<p style='font-size:64px; margin-bottom:8px;'>🍔</p>"
            "<p style='font-size:20px; font-weight:500;'>Set your preferences in the sidebar and hit Search!</p>"
            "</div>",
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
