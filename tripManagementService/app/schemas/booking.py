from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.utils.enums import RideStatus


class Location(BaseModel):
    latitude: float
    longitude: float

class BookingCreate(BaseModel):
    customer_id: str
    driver_id: str
    source_location: Location
    source_address: str
    destination_location: Location
    destination_address: str
    items: Optional[int] = None

class BookingResponse(BaseModel):
    id: str
    customer_id: str
    driver_id: str
    source_address: str
    source_location: Location
    destination_address: str
    destination_location: Location
    status: RideStatus
    items: Optional[int] = None
    startedAt: Optional[datetime] = None
    endedAt: Optional[datetime] = None
    created_at: datetime


class ActiveTripResponse(BaseModel):
    active_trip: BookingResponse
    tracking_token: Optional[str] = None


class CompletedTripResponse(BaseModel):
    completed_trips: Optional[List[BookingResponse]] = []