from enum import Enum

class GenderEnum(Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"


class VehicleType(Enum):
    BIKE = "Bike"
    MOTORBIKE = "Motorbike"
    SCOOTER = "Scooter"
    CAR = "Car"
    MINI_TRUCK = "Mini Truck"
    PICKUP_TRUCK = "Pickup Truck"
    LORRY = "Lorry"
    TRAILER = "Trailer"
    VAN = "Van"
    CONTAINER_TRUCK = "Container Truck"
    REFRIGERATED_TRUCK = "Refrigerated Truck"


class VehicleCapacity(Enum):
    pass