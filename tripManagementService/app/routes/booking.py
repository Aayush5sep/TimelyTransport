import jwt
import requests
from fastapi import APIRouter, Depends, HTTPException
from datetime import timedelta, timezone, datetime
from app.schemas.booking import BookingCreate, ActiveTripResponse, CompletedTripResponse
from app.models.booking import Booking
from app.database import DBFactory
from app.utils.dependencies import validate_token, generate_tracking_token
from app.config import settings


router = APIRouter()


async def create_new_booking(booking: BookingCreate):
    try:
        with DBFactory() as db:
            new_booking = Booking.create_booking(db, booking)
            # TODO: Publish to SQS for driver notification
            # await publish_to_sqs({"booking_id": new_booking.id})

            # Call location service to mark the driver as 'booked'
            access_token_data = {
                "user_id": new_booking.driver_id,
                "user": "internal",
                "exp": datetime.now(timezone.utc) + timedelta(days=7)
            }
            access_token = jwt.encode(
                access_token_data,
                settings.AUTH_UNIVERSAL_SECRET,
                algorithm=settings.ALGORITHM,
            )
            requests.post(
                f"{settings.LOCATION_SERVICE_URL}driver/status",
                params={"status": "booked"},
                headers={"token": access_token}
            )
            return new_booking
        
    except Exception as err:
        raise err


@router.post("/{booking_id}/start")
async def start_ride(booking_id: str, otp: str, user_details: dict = Depends(validate_token)):
    try:
        if user_details.get("user") != "driver":
            raise HTTPException(status_code=403, detail="Forbidden, unauthorized user")
        with DBFactory() as db:
            # Verify OTP (assuming OTP is stored somewhere securely)
            if otp != "123456":  # Replace with actual verification logic
                raise HTTPException(status_code=400, detail="Invalid OTP")
            updated_booking = Booking.update_booking_status(db, booking_id, "STARTED")
            return {"status": "Ride Started", "booking_id": updated_booking.id}

    except Exception as err:
        raise err
    

@router.get("/active", response_model=ActiveTripResponse)
async def get_active_trip(user_details: dict = Depends(validate_token)):
    try:
        with DBFactory() as db:
            if user_details.get("user") == "customer":
                active_trip = Booking.get_customer_active_trip(db, user_details.get("user_id"))
                if active_trip is None:
                    raise HTTPException(status_code=404, detail="No active trips found")
                tracking_token = generate_tracking_token(active_trip)
                return {"active_trip": active_trip, "tracking_token": tracking_token}
            elif user_details.get("user") == "driver":
                active_trip = Booking.get_driver_active_trip(db, user_details.get("user_id"))
                if active_trip is None:
                    raise HTTPException(status_code=404, detail="No active trips found")
                return {"active_trip": active_trip}
            
            raise HTTPException(status_code=403, detail="Forbidden")
    except Exception as err:
        raise err


@router.get("/completed", response_model=CompletedTripResponse)
async def get_completed_trips(user_details: dict = Depends(validate_token)):
    try:
        with DBFactory() as db:
            if user_details.get("user") == "customer":
                completed_trips = Booking.get_customer_completed_trips(db, user_details.get("user_id"))
                if completed_trips is None:
                    return []
                return completed_trips
            elif user_details.get("user") == "driver":
                completed_trips = Booking.get_driver_completed_trips(db, user_details.get("user_id"))
                if completed_trips is None:
                    return []
                return completed_trips
            
            raise HTTPException(status_code=403, detail="Forbidden")
    except Exception as err:
        raise err
    

@router.post("/{booking_id}/cancel")
async def cancel_trip(booking_id: str, user_details: dict = Depends(validate_token)):
    try:
        if user_details.get("user") != "customer":
            raise HTTPException(status_code=403, detail="Forbidden, unauthorized user")
        with DBFactory() as db:
            # Check if the booking exists and if user is the customer
            booking = Booking.get_booking_by_id(db, booking_id)
            if not booking or booking.customer_id != user_details.get("user_id"):
                raise HTTPException(status_code=400, detail="Invalid booking ID")
            
            # Update booking status to 'CANCELLED'
            updated_booking = Booking.update_booking_status(db, booking_id, "CANCELLED")
            
            # Call location service to mark the driver as 'available'
            access_token_data = {
                "user_id": updated_booking.driver_id,
                "user": "internal",
                "exp": datetime.now(timezone.utc) + timedelta(days=7)
            }
            access_token = jwt.encode(
                access_token_data,
                settings.AUTH_UNIVERSAL_SECRET,
                algorithm=settings.ALGORITHM,
            )
            requests.post(
                f"{settings.LOCATION_SERVICE_URL}driver/status",
                params={"status": "available"},
                headers={"token": access_token}
            )
            return {"status": "Trip Cancelled", "booking_id": updated_booking.id}

    except Exception as err:
        raise err