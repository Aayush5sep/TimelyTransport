import jwt
from fastapi import HTTPException, status, Header

from config import settings


def validate_token(token: str = Header(...)):
    try:
        # Step 1: Decode the token
        user_details = jwt.decode(
            token, settings.AUTH_UNIVERSAL_SECRET, algorithms=[settings.ALGORITHM]
        )

        # Step 2: Extract user ID from the decoded token, if None forbid it
        user_id = user_details.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Token"
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