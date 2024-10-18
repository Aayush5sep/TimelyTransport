from fastapi import APIRouter, HTTPException, status, Body, Depends

from app.database import DBFactory
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.schemas.vehicle import RegisterVehicleRequest, GetVehicleResponse, RegisterVehicleResponse
from app.utils.dependencies import validate_token


router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=RegisterVehicleResponse)
async def register_vehicle(
    vehicle_details: RegisterVehicleRequest = Body(...), driver_details: dict = Depends(validate_token)
):
    """
    Register a new vehicle for driver.

    :param vehicle_details: Vehicle details obtained from the request body.
    :param driver_details: Driver details obtained from the request header.

    :returns: A dictionary containing the details of the newly registered vehicle.

    :raises HTTPException 401 Unauthorized: If the driver is not authenticated.
    :raises HTTPException 409 Conflict: If a vehicle with the same registration number already exists.
    :raises HTTPException 422 Unprocessable Entity: If the vehicle details are not valid.
    """
    try:
        with DBFactory() as db:
            # Step 1: Check if vehicle with same registration number already exists
            existing_vehicle = Vehicle.get_vehicle_by_regno(db, vehicle_details.registration_number)
            if existing_vehicle is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Vehicle with registration number {vehicle_details.registration_number} already exists.",
                )

            # Step 2: Create a new vehicle
            new_vehicle_details = {
                "driver_id": driver_details.get("user_id"),
                "registration_number": vehicle_details.registration_number,
                "vehicle_type": vehicle_details.vehicle_type,
                "capacity": vehicle_details.capacity
            }
            new_vehicle = Vehicle.create_new_vehicle(db, **new_vehicle_details)

            # Step 3: Update vehicle id of driver
            updated_driver = Driver.update_vehicle_id(db, new_vehicle.driver_id, new_vehicle.id)
            # TODO: Update token using auth.py endpoint from FE

            return {
                "message": "Vehicle registered sucessfully.",
                "vehicle_details": new_vehicle
            }

    except Exception as err:
        raise err
    

@router.get("/{driver_id}/{vehicle_id}", status_code=status.HTTP_200_OK, response_model=GetVehicleResponse)
async def get_vehicle_details(driver_id: str, vehicle_id: str):
    """
    Get vehicle details.

    :param
    """
    try:
        with DBFactory() as db:
            vehicle_details = Vehicle.get_vehicle_by_driver_vehicle_id(db, vehicle_id, driver_id)
            if vehicle_details is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail = "Vehicle not found."
                )
            return vehicle_details

    except Exception as err:
        raise err