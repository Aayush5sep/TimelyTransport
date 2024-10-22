import jwt
import bcrypt
from datetime import datetime
from datetime import timedelta, timezone
from fastapi import APIRouter, HTTPException, status, Body

from app.config import settings
from app.database import DBFactory
from app.models.customer import Customer
from app.schemas.customer import RegisterCustomerRequest, LoginCustomerRequest, RegisterLoginCustomerResponse
from app.utils.helper_functions import add_country_code, hash_password, convert_ll_to_point


router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=RegisterLoginCustomerResponse)
async def register_customer(
    customer_details: RegisterCustomerRequest = Body(...)
):
    """
    Register a new customer by creating a new account.

    :param customer_details: User details obtained from the request body.

    :returns: A dictionary containing a success message and a JWT token upon successful registration.

    :raises HTTPException 409 Conflict: If a customer with the same phone number already exists.
    :raises HTTPException 422 Unprocessable Entity: If a customer with the phone number is not valid.
    :raises HTTPException 401 Unauthorized: If the provided OTP code is invalid.
    :raises HTTPException 500 Internal Server Error: If an unexpected error occurs during the registration process or while sending notification.
    """
    try:
        with DBFactory() as db:
            # Step 1: Check if a customer with the same phone number already exists
            existing_customer = Customer.get_user_by_phone(
                db, add_country_code(customer_details.phone_number)
            )
            # If user already exists, fallback to login 
            if existing_customer:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"User with phone number {existing_customer.phone_number} already exists.",
                )

            # Step 2: Create a new customer
            new_customer = {
                "name": customer_details.name or None,
                "phone_number": add_country_code(customer_details.phone_number),
                "email": customer_details.email or None,
                "password": hash_password(customer_details.password),
                "gender": customer_details.gender,
                "home_location": None,
                "home_address": customer_details.home_address or None,
            }
            if customer_details.home_location is not None:
                new_customer["home_location"] = convert_ll_to_point(
                    customer_details.home_location.latitude, customer_details.home_location.longitude
                )
            new_customer = Customer.create_new_customer(db, **new_customer)

            # Step 3: Generate JWT access token for authentication
            access_token_data = {
                "user_id": new_customer.id,
                "name": new_customer.name,
                "phone_number": new_customer.phone_number,
                "user": "customer",
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


@router.post("/login", status_code=status.HTTP_200_OK, response_model=RegisterLoginCustomerResponse)
async def login_customer(
    customer_login: LoginCustomerRequest = Body(...)
):
    """
    Authenticate a user by verifying the provided OTP code against stored credentials.

    :param customer_login: The phone number & password associated with the user.

    :returns: A dictionary containing a success message and a JWT token upon successful login.

    :raises HTTPException 404 Not Found: If no user is found with the provided phone number.
    :raises HTTPException 401 Unauthorized: If the provided OTP code is invalid.
    :raises HTTPException 500 Internal Server Error: If an unexpected error occurs during the login process.
    """
    try:
        with DBFactory() as db:
            # Step 1: Fetch customer details based on phone number; Raise error if customer does not exist
            customer_details = Customer.get_user_by_phone(
                db, add_country_code(customer_login.phone_number)
            )
            if not customer_details:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with phone number {customer_login.phone_number} not found.",
                )

            # Step 2: Validate password
            if not bcrypt.checkpw(customer_login.password.encode("utf-8"), str(customer_details.password).encode("utf-8")):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong phone number or password"
                )
            
            # Step 3: Generate JWT access token for authentication
            access_token_data = {
                "user_id": customer_details.id,
                "name": customer_details.name,
                "phone_number": customer_details.phone_number,
                "user": "customer",
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