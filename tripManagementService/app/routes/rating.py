import requests
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.rating import RatingCreate, DriverRatingsResponse, RatingResponse
from app.models.rating import Rating
from app.models.booking import Booking
from app.database import DBFactory
from app.config import settings
from app.utils.dependencies import validate_token

router = APIRouter()

@router.post("/", response_model=RatingResponse)
def submit_rating(rating_data: RatingCreate, user_details: dict = Depends(validate_token)):
    """
    Submit a rating for a completed trip. Verifies if the trip is marked as COMPLETED.
    """
    if user_details.get("user") != "customer" or user_details.get("user_id") != rating_data.customer_id:
        raise HTTPException(status_code=403, detail="Forbidden, unauthorized user")
    try:
        with DBFactory() as db:
            # Verify if the trip is completed
            trip = Booking.is_trip_completed(db, rating_data.trip_id)

            if not trip.status == "COMPLETED":
                raise HTTPException(status_code=400, detail="Cannot rate a trip that hasn't been completed.")

            prev_rating = Rating.get_rating_by_trip_id(db, rating_data.trip_id)
            if prev_rating:
                raise HTTPException(status_code=400, detail="Rating already submitted for this trip.")
            # Create and store the rating
            new_rating = Rating.create_rating(db, rating_data)
            # Update driver rating in auth service
            requests.post(
                f"{settings.AUTH_SERVICE_URL}driver/update-rating",
                params={"driver_id": rating_data.driver_id, "rating": rating_data.rating},
            )

            return new_rating
    
    except Exception as err:
        raise err
    

@router.get("/driver/{driver_id}", response_model=DriverRatingsResponse)
def fetch_driver_ratings(driver_id: str):
    """
    Get all ratings and the average rating for a specific driver.
    """
    try:
        with DBFactory() as db:
            ratings_data = Rating.get_driver_ratings(db, driver_id)
            return ratings_data
    
    except Exception as err:
        raise err