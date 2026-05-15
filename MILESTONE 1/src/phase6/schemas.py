from typing import List, Optional, Union
from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    location: str = Field(..., description="Preferred location (e.g., Bellandur).")
    budget: str = Field(..., description="Budget tier or amount (e.g., low, 800).")
    cuisine: str = Field(..., description="Preferred cuisine (e.g., North Indian, or Any).")
    min_rating: Union[str, float] = Field(
        ..., description="Minimum rating between 0 and 5."
    )
    additional_preferences: Optional[List[str]] = Field(
        default=[], description="Additional preferences (e.g., family-friendly)."
    )
    top_n: Optional[int] = Field(
        default=5, description="Number of recommendations to return."
    )
