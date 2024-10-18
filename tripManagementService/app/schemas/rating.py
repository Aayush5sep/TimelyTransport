from pydantic import BaseModel, Field
from typing import Optional, List

class RatingCreate(BaseModel):
    trip_id: str
    customer_id: str
    driver_id: str
    rating: int = Field(..., ge=1, le=5)
    feedback: Optional[str] = None

class RatingResponse(BaseModel):
    id: str
    trip_id: str
    customer_id: str
    driver_id: str
    rating: int
    feedback: Optional[str]

class DriverRatingsResponse(BaseModel):
    driver_id: str
    average_rating: float
    ratings: List[RatingResponse]