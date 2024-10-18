import jwt
from fastapi import HTTPException, status, Header

from app.config import settings
from app.database import DBFactory
from app.models.customer import Customer
from app.models.driver import Driver


def validate_token(token: str = Header(...)):
    try:
        # Step 1: Decode the token
        user_details = jwt.decode(
            token, settings.UNIVERSAL_SECRET, algorithms=[settings.ALGORITHM]
        )

        # Step 2: Extract user ID from the decoded token, if None forbid it
        user_id = user_details.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Token"
            )
        
        # Step 3: Check if the user exists in DB, if no raises an HTTPException with status code 401 Unauthorized else return the token for further processing
        user_type = user_details.get("user")
        customer = None
        driver = None
        with DBFactory() as db:
            # Step 3.1: Find user in customer table or driver table
            if user_type == "customer":
                customer = Customer.get_user_by_ID(db, user_id)
            elif user_type == "driver":
                driver = Driver.get_user_by_ID(db, user_id)

        if customer is None and driver is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )
        return user_details

    # Step 4: Handle exceptions
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token"
        )

    except Exception as e:
        raise e