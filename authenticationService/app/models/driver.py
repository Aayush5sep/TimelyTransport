import uuid
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Date, Float, Integer
from sqlalchemy.orm import Session

from app.database import Base
from app.utils.enums import GenderEnum
from app.utils.helper_functions import get_current_time
from app.models.vehicle import Vehicle


class Driver(Base):
    __tablename__ = "driver"

    id = Column(String(36), primary_key=True, default=str(uuid.uuid4()), unique=True, nullable=False, index=True)
    vehicle_id = Column(String(36), ForeignKey("vehicle.id"), nullable=True)
    name = Column(String(255), nullable=False)
    phone_number = Column(String(15), nullable=False)
    email = Column(String(255), nullable=True)
    password = Column(String(255), nullable=False)
    gender = Column(Enum(GenderEnum), nullable=False)
    dob = Column(Date, nullable=False)
    rating = Column(Float, nullable=False, default=5)
    rating_nos = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=get_current_time)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = self.id or str(uuid.uuid4())
        
    # Create Operations

    @classmethod
    def create_new_driver(cls, db: Session, **kwargs):
        new_driver = cls(**kwargs)
        db.add(new_driver)
        db.commit()
        db.refresh(new_driver)
        return new_driver

    # Read Operations

    @classmethod
    def get_user_by_phone(cls, db: Session, phone_number: str):
        return db.query(cls).filter(cls.phone_number == phone_number).first()
    
    @classmethod
    def get_user_by_ID(cls, db: Session, user_id: str):
        return db.query(cls).filter(cls.id == user_id).first()

    # Update Operations

    @classmethod
    def update_vehicle_id(cls, db: Session, user_id: str, vehicle_id: str):
        driver = db.query(cls).filter(cls.id == user_id).first()
        if driver is not None:
            setattr(driver, "vehicle_id", vehicle_id)
            db.commit()
            db.refresh(driver)
            return driver
        return None
    
    @classmethod
    def update_driver_rating(cls, db: Session, user_id: str, rating: float):
        driver = db.query(cls).filter(cls.id == user_id).first()
        if driver is not None:
            setattr(driver, "rating", rating)
            setattr(driver, "rating_nos", driver.rating_nos + 1)
            db.commit()
            db.refresh(driver)
            return driver
        return None

    # Delete Operations


def get_driver_rating_vehicle_type(db: Session, driver_id: str):
    """
    Fetch both the driver's rating and vehicle type in a single query using SQLAlchemy join.
    """
    # Perform a left outer join between Driver and Vehicle models
    result = (
        db.query(Driver, Vehicle.vehicle_type)
        .outerjoin(Vehicle, Vehicle.id == Driver.vehicle_id)
        .filter(Driver.id == driver_id)
        .first()
    )

    if not result:
        return None

    driver, vehicle_type = result

    # Prepare the response
    response = {
        "driver_id": driver.id,
        "rating": driver.rating,
        "vehicle_type": vehicle_type,
    }

    return response