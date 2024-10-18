from enum import Enum

class RideStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    STARTED = "STARTED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class PaymentMode(str, Enum):
    CASH = "CASH"
    CARD = "CARD"
    WALLET = "WALLET"

class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

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