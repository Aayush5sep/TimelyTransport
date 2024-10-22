import redis.asyncio as redis
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import List, Dict
import time
import asyncio

from schemas import LocationUpdate, ProximityQuery
from redis_client import get_redis
from helper_functions import get_driver_vehicle_type_rating
from dependencies import validate_auth_token, validate_tracking_token_ws, validate_auth_token_ws


router = APIRouter()
REDIS_KEY = "drivers:locations"


async def update_driver_location(
    driver_id: str, latitude: float, longitude: float, redis_client: redis.Redis
):
    """
    Add/Update a driver's location and metadata in Redis.
    """
    exists = await redis_client.exists(f"driver:{driver_id}")

    # Update location and timestamp
    await redis_client.geoadd(REDIS_KEY, (longitude, latitude, f"driver:{driver_id}"))
    await redis_client.hset(f"driver:{driver_id}", "timestamp", time.time())

    # If the driver does not exist, fetch vehicle type and rating
    if not exists:
        driver_details = await get_driver_vehicle_type_rating(driver_id)
        await redis_client.hset(
            f"driver:{driver_id}",
            mapping={
                "vehicle_type": driver_details.get("vehicle_type", ""),
                "rating": driver_details.get("rating", ""),
                "status": "available"
            }
        )


async def get_drivers_within_radius_with_filtering(
    latitude: float, longitude: float, radius: float, redis_client: redis.Redis, vehicle_type: str = None
) -> List[Dict]:
    """
    Query Redis to find drivers within a certain radius with filtering.
    """
    current_time = time.time()

    # Fetch nearby drivers using Redis GEO search
    nearby_drivers = await redis_client.geosearch(
        REDIS_KEY,
        longitude=longitude,
        latitude=latitude,
        radius=radius,
        unit="m",
        withdist=True,
        withcoord=True
    )

    results = []
    for (driver_id, distance, coords) in nearby_drivers:
        driver_data = await redis_client.hgetall(f"driver:{driver_id.decode('utf-8')}")

        # Validate and filter driver data
        if (
            driver_data and
            driver_data.get(b"status") == b"available" and  # Driver must be available
            (vehicle_type is None or driver_data.get(b"vehicle_type") == vehicle_type.encode('utf-8')) and
            current_time - float(driver_data.get(b"timestamp", 0)) < 30  # Must be recent
        ):
            latitude, longitude = coords
            results.append({
                "driver_id": driver_id.decode('utf-8'),
                "distance": distance,
                "latitude": latitude,
                "longitude": longitude,
                "vehicle_type": driver_data.get(b"vehicle_type", b"").decode('utf-8'),
                "rating": driver_data.get(b"rating", b"").decode('utf-8'),
                "status": driver_data.get(b"status", b"").decode('utf-8')
            })

    return results


@router.websocket("/ws/location")
async def websocket_endpoint(websocket: WebSocket, redis_client: redis.Redis = Depends(get_redis), user_details: dict = Depends(validate_auth_token_ws)):
    """
    WebSocket endpoint to receive location updates from multiple drivers.
    """
    if user_details.get("user") != "driver":
        raise HTTPException(status_code=403, detail="Unauthorized driver.")
    print("Waiting websocket acception")
    await websocket.accept()
    print("Websocket accepted")
    try:
        while True:
            print("Waiting to receive location update...")
            data = await websocket.receive_json()
            print(f"Received location update")
            location_update = LocationUpdate(**data)
            print(f"{location_update.driver_id} -> {location_update.latitude}, {location_update.longitude}")
            await update_driver_location(
                location_update.driver_id,
                location_update.latitude,
                location_update.longitude,
                redis_client,
            )
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for driver: {user_details.get('user_id')}")
        # await redis_client.hset(f"driver:{data.get('driver_id')}", "status", "unavailable") # Maybe activate it if very much sure of shared worker
    except Exception as e:
        websocket.close()
        raise e


@router.post("/update-location-manual")
async def update_location(location_update: LocationUpdate, redis_client: redis.Redis = Depends(get_redis), user_details: dict = Depends(validate_auth_token)):
    """
    Endpoint to receive location update on manual click.
    """
    if user_details.get("user") != "driver":
        raise HTTPException(status_code=403, detail="Unauthorized driver.")
    try:
        await update_driver_location(
            location_update.driver_id,
            location_update.latitude,
            location_update.longitude,
            redis_client,
        )
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/driver/status")
async def update_driver_status(status: str, redis_client: redis.Redis = Depends(get_redis), user_details: dict = Depends(validate_auth_token)):
    """
    Update the status of a driver (available/booked/unavailable).
    """
    if user_details.get("user") != "internal":
        raise HTTPException(status_code=403, detail="Unauthorized driver.")
    driver_id = user_details.get("user_id")
    if status not in ["available", "booked", "unavailable"]:
        raise HTTPException(status_code=400, detail="Invalid status.")

    exists = await redis_client.exists(f"driver:{driver_id}")
    if not exists:
        raise HTTPException(status_code=404, detail="Driver not found.")

    await redis_client.hset(f"driver:{driver_id}", "status", status)
    return {"message": f"Driver {driver_id} status updated to {status}."}


@router.post("/proximity")
async def get_nearby_drivers(query: ProximityQuery, redis_client: redis.Redis = Depends(get_redis), user_details: dict = Depends(validate_auth_token)):
    """
    API endpoint to get all closest drivers within a certain radius.
    """
    if user_details.get("user") != "customer":
        raise HTTPException(status_code=403, detail="Unauthorized customer.")
    drivers = await get_drivers_within_radius_with_filtering(
        query.latitude, query.longitude, query.radius, redis_client, query.vehicle_type
    )
    return {"drivers": drivers}


@router.websocket("/ws/driver-location")
async def websocket_driver_location(
    websocket: WebSocket,
    redis_client: redis.Redis = Depends(lambda: redis.Redis.from_url("redis://localhost")),
):
    """WebSocket route to provide driver location tracking."""
    # Accept the WebSocket connection first
    await websocket.accept()

    # Validate both tokens
    user_details = await validate_auth_token_ws(websocket)
    tracking_details = await validate_tracking_token_ws(websocket)

    if user_details.get("user") != "customer":
        raise HTTPException(status_code=403, detail="Unauthorized customer.")
    
    if tracking_details.get("customer_id") != user_details.get("user_id"):
        raise HTTPException(status_code=403, detail="Unauthorized customer.")

    driver_id = tracking_details["driver_id"]

    # Fetch driver data from Redis
    driver_data = await redis_client.hgetall(f"driver:{driver_id}")
    if not driver_data:
        raise HTTPException(status_code=404, detail="Driver not found.")
    driver_info = {
        "driver_id": driver_id,
        "vehicle_type": driver_data.get(b"vehicle_type", b"").decode("utf-8"),
        "rating": driver_data.get(b"rating", b"").decode("utf-8"),
        "status": driver_data.get(b"status", b"").decode("utf-8"),
    }
    
    try:
        while True:
            # Fetch driver location from Redis GeoSet
            location = await redis_client.geopos(REDIS_KEY, f"driver:{driver_id}")
            if not location or location[0] is None:
                raise HTTPException(status_code=404, detail="Driver location not found.")

            latitude, longitude = location[0]

            # Update driver location to send to the client
            driver_info["latitude"] = latitude
            driver_info["longitude"] = longitude

            # Send data to the WebSocket client
            await websocket.send_json(driver_info)

            # Wait 5 seconds before sending the next update
            await asyncio.sleep(5)

    except WebSocketDisconnect:
        print(f"WebSocket connection closed for driver {driver_id}")
    except Exception as e:
        print(f"Error: {e}")
        await websocket.close()