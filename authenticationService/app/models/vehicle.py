import uuid
from sqlalchemy import Column, String, Enum, ForeignKey, and_
from sqlalchemy.orm import Session

from app.database import Base
from app.utils.enums import VehicleType


class Vehicle(Base):
    __tablename__ = "vehicle"

    id = Column(String(36), primary_key=True, default=str(uuid.uuid4()), unique=True, nullable=False, index=True)
    driver_id = Column(String(36), ForeignKey("driver.id", ondelete="CASCADE"), nullable=False)
    registration_number = Column(String(20), nullable=False)
    vehicle_type = Column(Enum(VehicleType), nullable=False)
    capacity = Column(String(36), nullable=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = self.id or str(uuid.uuid4())
                
    # Create Operations

    @classmethod
    def create_new_vehicle(cls, db: Session, **kwargs):
        new_vehicle = cls(**kwargs)
        db.add(new_vehicle)
        db.commit()
        db.refresh(new_vehicle)
        return new_vehicle

    # Read Operations

    @classmethod
    def get_vehicle_by_regno(cls, db: Session, regno: str):
        db.query(cls).filter(cls.registration_number == regno).first()

    @classmethod
    def get_vehicle_by_driver_vehicle_id(cls, db: Session, vehicle_id: str, driver_id: str):
        db.query(cls).filter(and_(cls.id == vehicle_id, cls.driver_id == driver_id)).first()

    # Update Operations

    # Delete Operations