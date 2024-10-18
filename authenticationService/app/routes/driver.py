import jwt
import bcrypt
from datetime import datetime
from datetime import timedelta, timezone
from fastapi import APIRouter, HTTPException, status, Body

from app.config import settings
from app.database import DBFactory
from app.models.driver import Driver, get_driver_rating_vehicle_type
from app.schemas.driver import RegisterDriverRequest, LoginDriverRequest, RegisterLoginDriverResponse
from app.utils.helper_functions import add_country_code, hash_password


router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=RegisterLoginDriverResponse)
async def register_driver(
    driver_details: RegisterDriverRequest = Body(...)
):
    """
    Register a new driver by creating a new account.

    :param driver_details: User details obtained from the request body.

    :returns: A dictionary containing a success message and a JWT token upon successful registration.

    :raises HTTPException 409 Conflict: If a driver with the same phone number already exists.
    :raises HTTPException 422 Unprocessable Entity: If a driver with the phone number is not valid.
    :raises HTTPException 401 Unauthorized: If the provided OTP code is invalid.
    :raises HTTPException 500 Internal Server Error: If an unexpected error occurs during the registration process or while sending notification.
    """
    try:
        with DBFactory() as db:
            # Step 1: Check if a driver with the same phone number already exists
            existing_driver = Driver.get_user_by_phone(
                db, add_country_code(driver_details.phone_number)
            )
            # If user already exists, fallback to login 
            if existing_driver:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"User with phone number {existing_driver.phone_number} already exists.",
                )

            # Step 2: Create a new driver
            new_driver = {
                "name": driver_details.name,
                "phone_number": add_country_code(driver_details.phone_number),
                "email": driver_details.email or None,
                "password": hash_password(driver_details.password),
                "gender": driver_details.gender,
                "dob": driver_details.dob,
            }
            new_driver = Driver.create_new_driver(db, **new_driver)

            # Step 3: Generate JWT access token for authentication
            access_token_data = {
                "user_id": new_driver.get("id"),
                "name": new_driver.get("name"),
                "phone_number": new_driver.get("phone_number"),
                "vehicle_id": new_driver.get("vehicle_id"),
                "user": "driver",
                "exp": datetime.now(timezone.utc) + timedelta(days=7),
            }
            access_token = jwt.encode(
                access_token_data,
                key=settings.UNIVERSAL_SECRET,
                algorithm=settings.ALGORITHM,
            )

            # Step 4: Return success message and access token
            return {
                "message": "Account created successfully",
                "access_token": access_token,
            }

    except Exception as err:
        raise err


@router.post("/login", status_code=status.HTTP_200_OK, response_model=RegisterLoginDriverResponse)
async def login_driver(
    driver_login: LoginDriverRequest = Body(...)
):
    """
    Authenticate a user by verifying the provided OTP code against stored credentials.

    :param driver_login: The phone number & password associated with the user.

    :returns: A dictionary containing a success message and a JWT token upon successful login.

    :raises HTTPException 404 Not Found: If no user is found with the provided phone number.
    :raises HTTPException 401 Unauthorized: If the provided OTP code is invalid.
    :raises HTTPException 500 Internal Server Error: If an unexpected error occurs during the login process.
    """
    try:
        with DBFactory() as db:
            # Step 1: Fetch driver details based on phone number; Raise error if driver does not exist
            driver_details = Driver.get_user_by_phone(
                db, add_country_code(driver_login.phone_number)
            )
            if not driver_details:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with phone number {driver_login.phone_number} not found.",
                )

            # Step 2: Validate password
            if not bcrypt.checkpw(driver_login.password.encode("utf-8"), str(driver_details.password).encode("utf-8")):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong phone number or password"
                )
            
            # Step 3: Generate JWT access token for authentication
            access_token_data = {
                "user_id": driver_details.id,
                "name": driver_details.name,
                "phone_number": driver_details.phone_number,
                "vehicle_id": driver_details.vehicle_id,
                "user": "driver",
                "exp": datetime.now(timezone.utc) + timedelta(days=7),
            }
            access_token = jwt.encode(
                access_token_data,
                key=settings.UNIVERSAL_SECRET,
                algorithm=settings.ALGORITHM,
            )

            # Step 4: Return success message and access token
            return {
                "message": "Login successful",
                "access_token": access_token,
            }

    except Exception as err:
        raise err
    

@router.put("/update-rating", status_code=status.HTTP_200_OK)
async def update_driver_rating(
    driver_id: int, rating: int
):
    """
    Update the rating of a driver.

    :param driver_id: The ID of the driver whose rating is to be updated.
    :param rating: The new rating value to be adjusted to the driver's rating.

    :returns: A dictionary containing a success message upon successful rating update.

    :raises HTTPException 404 Not Found: If no driver is found with the provided ID.
    :raises HTTPException 500 Internal Server Error: If an unexpected error occurs during the rating update process.
    """
    try:
        with DBFactory() as db:
            # Step 1: Fetch driver details based on driver ID; Raise error if driver does not exist
            driver_details = Driver.get_user_by_ID(db, driver_id)
            if not driver_details:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Driver with ID {driver_id} not found.",
                )

            # Step 2: Calculate new average rating
            total_ratings = driver_details.rating_nos
            current_rating = driver_details.rating
            new_rating = (current_rating * total_ratings + rating) / (total_ratings + 1)

            # Step 3: Update driver rating and increment number of ratings
            updated_driver = Driver.update_driver_rating(db, driver_id, new_rating)
            if updated_driver is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to update driver rating.",
                )

            # Step 4: Return success message
            return {
                "message": "Driver rating updated successfully",
            }

    except Exception as err:
        raise err
    

@router.get("/info/{driver_id}")
def get_driver_vehicle_info(driver_id: str):
    """
    Fetch both the driver's rating and vehicle type in a single query using SQLAlchemy join.
    """
    try:
        with DBFactory() as db:
            response = get_driver_rating_vehicle_type(db, driver_id)
            if response is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Driver with ID {driver_id} not found.",
                )

            return response
        
    except Exception as err:
        raise err