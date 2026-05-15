import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from src.phase2.validators import validate_preferences
from src.phase3.retrieval import RetrievalConfig, retrieve_candidates
from src.phase4.engine import generate_recommendations
from src.phase5.formatter import format_final_response
from .schemas import RecommendationRequest

logger = logging.getLogger(__name__)

# Global reference to keep dataset in memory
app_state: Dict[str, Any] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load restaurants dataset into memory on startup
    csv_path = Path("data/processed/restaurants_clean.csv")
    if not csv_path.exists():
        logger.error(f"Dataset not found at {csv_path}. Please run Phase 1.")
        raise FileNotFoundError(f"Missing {csv_path}")
        
    try:
        df = pd.read_csv(csv_path)
        if "budget_tier" not in df.columns:
            def _cost_to_budget_tier(cost_for_two: float) -> str:
                if cost_for_two < 600:
                    return "low"
                if cost_for_two <= 1500:
                    return "medium"
                return "high"
            
            costs = pd.to_numeric(df["cost_for_two"], errors="coerce").fillna(0.0)
            df["budget_tier"] = costs.apply(_cost_to_budget_tier)
        
        app_state["restaurants"] = df

        # Pre-compute available locations for the /locations endpoint
        locations = sorted(
            df["location"].astype(str).str.strip().unique().tolist()
        )
        app_state["locations"] = [loc for loc in locations if loc and loc != "nan"]

        logger.info(f"Loaded {len(app_state['restaurants'])} restaurants into memory.")
    except Exception as e:
        logger.error(f"Error loading dataset: {e}")
        raise
        
    yield
    
    # Cleanup on shutdown
    app_state.clear()


app = FastAPI(
    title="AI Restaurant Recommender API",
    description="Backend service for restaurant recommendations (Phase 6).",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware to allow requests from the future Phase 7 frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """Health check endpoint for monitoring."""
    restaurants_df = app_state.get("restaurants")
    return {
        "status": "healthy",
        "restaurants_loaded": len(restaurants_df) if restaurants_df is not None else 0,
        "locations_available": len(app_state.get("locations", [])),
    }


@app.get("/api/v1/locations", status_code=status.HTTP_200_OK)
async def list_locations() -> Dict[str, List[str]]:
    """Return available locations from the dataset for frontend autocomplete."""
    return {"locations": app_state.get("locations", [])}


@app.post("/api/v1/recommendations", status_code=status.HTTP_200_OK)
async def get_recommendations(req: RecommendationRequest) -> Dict[str, Any]:
    """
    Generate top-N restaurant recommendations based on user preferences.
    Executes Phases 2 through 5 of the recommendation pipeline.
    """
    # 1. Phase 2: Validate preferences
    try:
        preference_obj = validate_preferences(
            location=req.location,
            budget=req.budget,
            cuisine=req.cuisine,
            min_rating=req.min_rating,
            additional_preferences=req.additional_preferences,
        )
        preferences_dict = preference_obj.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    # 2. Phase 3: Candidate Retrieval
    restaurants_df = app_state.get("restaurants")
    if restaurants_df is None:
        raise HTTPException(status_code=500, detail="Database not loaded.")
        
    try:
        config = RetrievalConfig(max_candidates=30)
        retrieval_result = retrieve_candidates(
            restaurants=restaurants_df, 
            preferences=preferences_dict, 
            config=config
        ).to_dict()
    except Exception as e:
        logger.error(f"Phase 3 Retrieval Error: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving candidates.")

    # 3. Phase 4: LLM Recommendation
    try:
        candidates = retrieval_result.get("candidates", [])
        recommendation_result = generate_recommendations(
            preferences=preferences_dict,
            candidates=candidates,
            top_n=req.top_n,
        )
    except Exception as e:
        logger.error(f"Phase 4 LLM Error: {e}")
        raise HTTPException(status_code=500, detail="Error generating recommendations.")

    # 4. Phase 5: Response Formatting
    try:
        final_response = format_final_response(
            recommendation_result.to_dict(), 
            top_n=req.top_n
        ).to_dict()
    except Exception as e:
        logger.error(f"Phase 5 Formatting Error: {e}")
        raise HTTPException(status_code=500, detail="Error formatting final response.")

    return final_response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.phase6.main:app", host="0.0.0.0", port=8000, reload=True)
