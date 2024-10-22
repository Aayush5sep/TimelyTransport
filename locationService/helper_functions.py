import requests

from config import settings


async def get_driver_vehicle_type_rating(driver_id: str):
    """
    Fetch driver details from the driver service.
    """
    response = requests.get(f"{settings.AUTH_SERVICE_URL}{driver_id}")
    response.raise_for_status()
    return response.json()