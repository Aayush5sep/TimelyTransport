import uuid
from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.orm import Session
from geoalchemy2 import Geometry

from app.database import Base
from app.utils.enums import GenderEnum
from app.utils.helper_functions import get_current_time


class Customer(Base):
    __tablename__ = "customer"

    id = Column(String(36), primary_key=True, default=str(uuid.uuid4()), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    phone_number = Column(String(15), nullable=False)
    email = Column(String(255), nullable=True)
    password = Column(String(255), nullable=False)
    gender = Column(Enum(GenderEnum), nullable=False)
    home_address = Column(String(255), nullable=True)
    home_location = Column(Geometry('POINT', srid=4326), nullable=True)
    created_at = Column(DateTime, nullable=False, default=get_current_time)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = self.id or str(uuid.uuid4())

    # Create Operations

    @classmethod
    def create_new_customer(cls, db: Session, **kwargs):
        new_customer = cls(**kwargs)
        db.add(new_customer)
        db.commit()
        db.refresh(new_customer)
        return new_customer

    # Read Operations

    @classmethod
    def get_user_by_phone(cls, db: Session, phone_number: str):
        return db.query(cls).filter(cls.phone_number == phone_number).first()
    
    @classmethod
    def get_user_by_ID(cls, db: Session, user_id: str):
        return db.query(cls).filter(cls.id == user_id).first()

    # Update Operations

    # Delete Operations