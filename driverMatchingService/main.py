import httpx
import re
import warnings
import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict

from config import settings
from schemas import RequestBooking, DriverResponse
from redis_client import set_trip_status, unlock_driver
from dependencies import validate_token, validate_token_ws

# Ignore Deprecation Warnings (Optional)
warnings.filterwarnings("ignore", category=DeprecationWarning)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# Track active connections and tasks
active_connections: Dict[str, WebSocket] = {}
active_tasks: Dict[str, asyncio.Task] = {}


async def cancel_task_if_active(user_id: str):
    """Cancel the running task if the customer disconnects."""
    if user_id in active_tasks:
        active_tasks[user_id].cancel()
        del active_tasks[user_id]


async def notify_via_ws(user_id: str, message: dict):
    """Send a message via WebSocket."""
    if user_id in active_connections:
        websocket = active_connections[user_id]
        await websocket.send_json(message)


async def get_nearby_drivers_from_service(latitude, longitude, radius, vehicle_type=None):
    """Call the Proximity Service to get nearby drivers."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "radius": radius,
        "vehicle_type": vehicle_type,
    }

    async with httpx.AsyncClient() as client:
        for attempt in range(3):
            try:
                response = await client.post(settings.LOCATION_SERVICE_URL, json=params)
                response.raise_for_status()
                return response.json().get("drivers", [])
            except httpx.HTTPStatusError as err:
                print(f"Proximity service error: {err}")
            except httpx.RequestError as err:
                print(f"Request error: {err}")

            await asyncio.sleep(2 ** attempt + (0.1 * attempt))

    return []

from drivers import match_and_notify

@app.websocket("/ws/request-booking")
async def websocket_request_booking(websocket: WebSocket):
    """WebSocket connection for customer booking."""
    user_details: dict = await validate_token_ws(websocket)
    if user_details.get("user") != "customer":
        raise HTTPException(status_code=403, detail="Only logged in customers are allowed.")
    user_id = user_details.get("user_id")
    await websocket.accept()
    active_connections[user_id] = websocket  # Register customer connection

    try:
        # Receive the booking request
        booking_request = await websocket.receive_json()
        booking = RequestBooking(**booking_request)
        booking.user_id = user_id

        # Get nearby drivers
        nearby_drivers = await get_nearby_drivers_from_service(
            booking.source_location.latitude,
            booking.source_location.longitude,
            radius=2000,
            vehicle_type=booking.vehicle_type,
        )

        if not nearby_drivers:
            await websocket.send_json({"status": "failed", "message": "No drivers available nearby."})
            return

        # Start matching drivers and notify them
        task = asyncio.create_task(
            match_and_notify(nearby_drivers, booking)
        )
        active_tasks[user_id] = task

        # Wait for the task to complete
        await task

    except WebSocketDisconnect:
        # Handle customer disconnect
        await cancel_task_if_active(user_id)
        active_connections.pop(user_id, None)

    finally:
        # Clean up connections and tasks
        active_connections.pop(user_id, None)
        await cancel_task_if_active(user_id)


@app.post("/driver/response")
async def driver_response(response: DriverResponse, background_tasks: BackgroundTasks, user_details: dict = Depends(validate_token)):
    """Handle driver responses (accept/deny) and update Redis status."""
    if response.driver_id != user_details.get("user_id"):
        raise HTTPException(status_code=403, detail="Unauthorized driver response.")
    trip_id = f"{response.customer_id}+{response.driver_id}"

    # Check if the customer is connected via WebSocket
    if response.customer_id in active_connections:
        websocket = active_connections[response.customer_id]

        if response.status == "accepted":
            # Save trip status as 'accepted' in Redis with a TTL of 5 minutes
            await set_trip_status(trip_id, "accepted", 300)

            # Notify the customer via WebSocket
            await websocket.send_text(f"Accepted: Driver accepted your trip.")
            return {"message": "Trip accepted and status updated in Redis."}

        elif response.status == "denied":
            # Unlock the driver asynchronously
            background_tasks.add_task(unlock_driver, response.driver_id)
            return {"message": "Trip denied and status updated in Redis."}

    # If the customer is not connected via WebSocket
    raise HTTPException(status_code=400, detail="Invalid status or customer not connected.")


async def fetch_ola_distance_data(origin, destination):
    """Fetch distance data from Ola Distance API."""
    params = {
        "origins": f"{origin.latitude},{origin.longitude}",
        "destinations": f"{destination.latitude},{destination.longitude}",
        "mode": "driving",
        "api_key": "OyIE1iZDygLFJkrzgVxKLeufCGHd3UHLblmHWFSa",
        # "api_key": settings.OLA_API_KEY,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.olamaps.io/routing/v1/distanceMatrix", params=params)
        # response = await client.get(settings.OLA_DISTANCE_API_URL, params=params)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch route data")
        return response.json()
    

BASE_FARE = 50  # Base fare in currency units
FARE_PER_KM = 10

@app.post("/eta-fare")
async def get_eta_fare(booking_details: RequestBooking, user_details: dict = Depends(validate_token)):
    """Calculate ETA and Fare."""
    if user_details.get("user") != "customer":
        raise HTTPException(status_code=403, detail="Only logged in customers are allowed.")
    origin = booking_details.source_location
    destination = booking_details.destination_location

    # Fetch data from Ola Distance API
    route_data = await fetch_ola_distance_data(origin, destination)

    if route_data["status"] != "SUCCESS":
        raise HTTPException(status_code=500, detail="Route calculation failed")

    # Extract duration and distance from the response
    route = route_data["rows"][0]["elements"][0]
    distance_m = route["distance"]
    duration_seconds = route["duration"]

    # Calculate fare
    fare = BASE_FARE + (FARE_PER_KM * distance_m)

    return {
        "distance": round(distance_m, 2),
        "eta": round(duration_seconds, 2),
        "fare": round(fare, 2)
    }