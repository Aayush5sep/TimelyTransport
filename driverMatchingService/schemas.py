from pydantic import BaseModel
from typing import Optional


class Location(BaseModel):
    latitude: float
    longitude: float


class RequestBooking(BaseModel):
    user_id: Optional[str] = None
    source_location: Location
    source_address: Optional[str] = None
    destination_location: Location
    destination_address: Optional[str] = None
    vehicle_type: Optional[str] = None


class DriverResponse(BaseModel):
    customer_id: str
    driver_id: str
    status: str