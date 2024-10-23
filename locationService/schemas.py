from pydantic import BaseModel
from typing import Optional


class LocationUpdate(BaseModel):
    driver_id: str
    latitude: float
    longitude: float


class ProximityQuery(BaseModel):
    latitude: float
    longitude: float
    radius: float
    vehicle_type: Optional[str] = None