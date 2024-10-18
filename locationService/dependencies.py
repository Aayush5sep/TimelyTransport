import jwt
from fastapi import HTTPException, status, Header, WebSocket

from config import settings


def validate_auth_token(token: str = Header(...)):
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
    

async def validate_tracking_token_ws(websocket: WebSocket):
    token = websocket.query_params.get("tracking_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token missing")
    
    try:
        # Step 1: Decode the token
        tracking_details = jwt.decode(
            token, settings.REALTIME_TRACKING_SECRET, algorithms=[settings.ALGORITHM]
        )
        
        return tracking_details

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
    

async def validate_auth_token_ws(websocket: WebSocket):
    """Extract token from query params and validate it."""
    token = websocket.query_params.get("token")
    if not token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token missing")

    try:
        # Validate and decode the token
        user_details = jwt.decode(
            token, settings.AUTH_UNIVERSAL_SECRET, algorithms=[settings.ALGORITHM]  # Replace with your settings
        )

        user_id = user_details.get("user_id")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")

        return user_details

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")