from pydantic import BaseModel

from app.utils.enums import VehicleType


class RegisterVehicleRequest(BaseModel):
    registration_number: str
    vehicle_type : VehicleType
    capacity: str


class GetVehicleResponse(BaseModel):
    id: str
    driver_id: str
    registration_number: str
    vehicle_type : VehicleType
    capacity: str


class RegisterVehicleResponse(BaseModel):
    message: str