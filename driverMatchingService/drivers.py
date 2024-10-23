import asyncio
import httpx
from notifications import notify_driver
from redis_client import set_driver_state, get_driver_state, unlock_driver, check_trip_status
from schemas import RequestBooking
from config import settings
from main import notify_via_ws


async def create_trip(driver_id: str, booking_details: RequestBooking):
    """Create a new trip using the Trip Management Service."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                settings.TRIP_MANAGEMENT_SERVICE_URL,
                json={
                    "driver_id": driver_id,
                    "customer_id": booking_details.user_id,
                    "source_location": booking_details.source_location.model_dump(),
                    "destination_location": booking_details.destination_location.model_dump(),
                    "source_address": booking_details.source_address,
                    "destination_address": booking_details.destination_address,
                },
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            print(f"Failed to create trip: {exc.response.status_code}")
            raise
        except httpx.RequestError as exc:
            print(f"Error in trip request: {str(exc)}")
            raise


async def match_and_notify(nearby_drivers, booking_details: RequestBooking):
    """Match available drivers and notify them one-by-one until one accepts."""

    for driver in nearby_drivers:
        driver_id = driver["driver_id"]

        # Check if the driver is free
        if await get_driver_state(driver_id) == "free":
            # Lock the driver
            await set_driver_state(driver_id, "locked", 20)  # Set to locked before notifying

            # Notify the driver
            await notify_driver(
                driver_id=driver_id,
                customer_details=booking_details.model_dump(),
            )

            # Wait for the driver's response
            await asyncio.sleep(15)

            # Check if the driver accepted the trip
            temp_trip_id = f"{booking_details.user_id}+{driver_id}"
            if await check_trip_status(temp_trip_id):
                # Driver accepted; create the trip via HTTP request to Trip Management Service
                await notify_via_ws(
                    booking_details.user_id,
                    {"status": "success", "message": "Driver accepted the trip request."},
                )
                await create_trip(driver_id, booking_details)
                await set_driver_state(driver_id, "busy", 120)
                return  # Exit after successful trip creation

            # Unlock the driver if they did not accept
            await unlock_driver(driver_id)

    # Notify the customer if no driver accepted the trip
    await notify_via_ws(
        booking_details.user_id, 
        {"status": "failed", "message": "No driver accepted the trip request."}
    )