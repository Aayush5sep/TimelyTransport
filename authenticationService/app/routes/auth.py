import jwt
from datetime import datetime
from datetime import timedelta, timezone
from fastapi import APIRouter, HTTPException, Depends, status

from app.config import settings
from app.database import DBFactory
from app.models.customer import Customer
from app.models.driver import Driver
from app.utils.dependencies import validate_token


router = APIRouter()


@router.get("/profile", status_code=status.HTTP_200_OK)
async def get_user_profile(user_details: dict = Depends(validate_token)):
    """
    Fetches the user profile details based on the user_id and user_type provided in the access token.

    :param user_details: User details obtained from the validate_token dependency.

    :returns: User profile details dictionary.

    :raises HTTPException 401 Unauthorized: If the user is invalid.
    :raises HTTPException 500 Internal Server Error: If an unexpected error occurs during the user profile fetch process.
    """
    try:
        with DBFactory() as db:
            # Step 1: Fetch user details from the database for both customer & driver based on user_type
            user_type = user_details.get("user")
            user = None
            if user_type == "customer":
                user = Customer.get_user_by_ID(db, user_details.get("user_id"))
            elif user_type == "driver":
                user = Driver.get_user_by_ID(db, user_details.get("user_id"))

            # Step 2: Check if user exists or not
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user"
                )

            # Step 3: Prepare user profile details and return it
            user_profile = {
                "user_id": user.id,
                "name": user.name,
                "phone_number": user.phone_number,
                "email": user.email,
                "user": user_type
            }
            if user_type == "driver":
                user_profile["vehicle_id"] = user.vehicle_id

            return user_profile

    # Step 4: Handle exceptions
    except Exception as err:
        raise err


@router.post("/refresh-token", status_code=status.HTTP_200_OK, response_description='{"access_token": access_token}')
async def refresh_access_token(user_details: dict = Depends(validate_token)):
    """
    Generates a new access token using the refresh token provided in the request header.

    :param user_details: User details obtained from the validate_token dependency.

    :returns: A dictionary containing a new access token.

    :raises HTTPException 401 Unauthorized: If the user is invalid OR refresh token has expired.
    :raises HTTPException 403 Forbidden: If the refresh token is invalid.
    :raises HTTPException 500 Internal Server Error: If an unexpected error occurs during the token refresh process.

    """
    try:
        with DBFactory() as db:
            # Step 1: Fetch user details from the database for both customer & driver based on user_type
            user_type = user_details.get("user")
            user = None
            if user_type == "customer":
                user = Customer.get_user_by_ID(db, user_details.get("user_id"))
            else:
                user = Driver.get_user_by_ID(db, user_details.get("user_id"))

            # Step 2: Check if user exists or not
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user"
                )

            # Step 3: Set expiration time for the token, the token will expire after 7 days from now
            access_token_exp_time = datetime.now(timezone.utc) + timedelta(days=7)

            # Step 4: Include 'exp' claim in the token_data
            access_token_data = {
                "user_id": user_details.get("user_id"),
                "name": user.name,
                "phone_number": user.phone_number,
                "user": user_type,
                "exp": access_token_exp_time
            }
            if user_type == "driver":
                access_token_data["vehicle_id"] = user.vehicle_id

            # Step 5: Generate a new access token and return it
            access_token = jwt.encode(
                access_token_data,
                settings.UNIVERSAL_SECRET,
                algorithm=settings.ALGORITHM,
            )
            return {"access_token": access_token}

    # Step 6: Handle exceptions
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token"
        )

    except Exception as err:
        raise err


@router.get("/validate_token", status_code=status.HTTP_200_OK)
async def validate_user_token(user_details: dict = Depends(validate_token)):
    """
    Validates the access token provided in the request header for external services for validation.

    :param user_details: User details obtained from the validate_token dependency.

    :returns: User details dictionary.

    :raises HTTPException 500 Internal Server Error: If an unexpected error occurs during the token validation process.
    """
    return user_details