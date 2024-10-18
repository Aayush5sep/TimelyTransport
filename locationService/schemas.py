from pydantic import BaseModel


class LocationUpdate(BaseModel):
    driver_id: str
    latitude: float
    longitude: float


class ProximityQuery(BaseModel):
    latitude: float
    longitude: float
    radius: float
    vehicle_type: str