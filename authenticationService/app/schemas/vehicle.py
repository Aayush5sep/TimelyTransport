from pydantic import BaseModel

from app.utils.enums import VehicleCapacity, VehicleType


class RegisterVehicleRequest(BaseModel):
    registration_number: str
    vehicle_type : VehicleType
    capacity: VehicleCapacity


class GetVehicleResponse(BaseModel):
    id: str
    driver_id: str
    registration_number: str
    vehicle_type : VehicleType
    capacity: VehicleCapacity


class RegisterVehicleResponse(BaseModel):
    message: str
    vehicle_details: GetVehicleResponse