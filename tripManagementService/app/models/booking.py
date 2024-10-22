import uuid
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Date, Integer
from sqlalchemy.orm import Session
from geoalchemy2 import Geometry

from app.database import Base
from app.utils.helper_functions import get_current_time
from app.schemas.booking import BookingCreate
from app.utils.enums import RideStatus


class Booking(Base):
    __tablename__ = "booking"

    id = Column(String(36), primary_key=True, default=str(uuid.uuid4()), unique=True, nullable=False)
    customer_id = Column(String(36), nullable=False)
    driver_id = Column(String(36), nullable=False)
    payment_id = Column(String(36), nullable=True)
    source_location = Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)
    source_address = Column(String(255), nullable=False)
    destination_location = Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)
    destination_address = Column(String(255), nullable=False)
    status = Column(Enum(RideStatus), nullable=False)
    items = Column(Integer, nullable=True)
    startedAt = Column(DateTime, nullable=True)
    endedAt = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=get_current_time)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = self.id or str(uuid.uuid4())

    @classmethod
    def create_booking(cls, db: Session, booking: BookingCreate):
        new_booking = cls(**booking.model_dump(), status="ACCEPTED")
        db.add(new_booking)
        db.commit()
        db.refresh(new_booking)
        return new_booking

    @classmethod
    def update_booking_status(cls, db: Session, booking_id: str, status: str):
        booking = db.query(cls).filter(cls.id == booking_id).first()
        if not booking:
            raise ValueError("Booking not found")
        booking.status = status
        db.commit()
        db.refresh(booking)
        return booking
    
    @classmethod
    def is_trip_completed(cls, db: Session, booking_id: str):
        booking = db.query(cls).filter(cls.id == booking_id).first()
        return booking
    
    @classmethod
    def get_customer_active_trip(cls, db: Session, user_id: str):
        return db.query(cls).filter(cls.customer_id == user_id, cls.status != "COMPLETED").first()
    
    @classmethod
    def get_driver_active_trip(cls, db: Session, user_id: str):
        return db.query(cls).filter(cls.driver_id == user_id, cls.status != "COMPLETED").first()
    
    @classmethod
    def get_customer_completed_trips(cls, db: Session, user_id: str):
        return db.query(cls).filter(cls.customer_id == user_id, cls.status == "COMPLETED").all()
    
    @classmethod
    def get_driver_completed_trips(cls, db: Session, user_id: str):
        return db.query(cls).filter(cls.driver_id == user_id, cls.status == "COMPLETED").all()
    
    @classmethod
    def get_booking_by_id(cls, db: Session, booking_id: str):
        return db.query(cls).filter(cls.id == booking_id).first()