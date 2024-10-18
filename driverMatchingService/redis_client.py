import redis.asyncio as redis
from config import settings

# Initialize Redis client
# redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
redis_client = None

async def set_driver_state(driver_id: str, state: str, expiry: int = 60):
    """Set the driver state in Redis."""
    driver_state_key = f"driver:{driver_id}:state"
    await redis_client.set(driver_state_key, state, ex=expiry)

async def get_driver_state(driver_id: str) -> str:
    """Get the driver state from Redis, defaulting to 'free' if not found."""
    driver_state_key = f"driver:{driver_id}:state"
    state = await redis_client.get(driver_state_key)
    return state if state else "free"

async def unlock_driver(driver_id: str):
    """Unlock the driver after denial or cancellation."""
    await set_driver_state(driver_id, "free")  # Change state to free

async def set_trip_status(trip_id, status, expiry=600):
    """Set the trip status in Redis."""
    status_key = f"trip:{trip_id}:status"
    await redis_client.set(status_key, status, ex=expiry)

async def check_trip_status(trip_id):
    """Poll Redis to see if the trip is accepted."""
    status_key = f"trip:{trip_id}:status"
    status = await redis_client.get(status_key)
    return status == "accepted"