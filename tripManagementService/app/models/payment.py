import uuid
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Float
from sqlalchemy.orm import Session

from app.database import Base
from app.utils.helper_functions import get_current_time
from app.schemas.payment import PaymentCreate


class Payment(Base):
    __tablename__ = "payment"

    id = Column(String(36), primary_key=True, default=str(uuid.uuid4()), unique=True, nullable=False)
    trip_id = Column(String(36), ForeignKey("booking.id"), nullable=False)
    third_party_reference = Column(String(36), nullable=True)
    amount = Column(Float, nullable=False)
    mode = Column(String(36), nullable=False)
    status = Column(String(36), nullable=False)
    created_at = Column(DateTime, nullable=False, default=get_current_time)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = self.id or str(uuid.uuid4())

    @classmethod
    def create_payment(cls, db: Session, payment: PaymentCreate):
        new_payment = cls(**payment.model_dump(), status="PENDING")
        db.add(new_payment)
        db.commit()
        db.refresh(new_payment)
        return new_payment
    
    @classmethod
    def update_payment_status(cls, db: Session, payment_id: str, status: str):
        payment = db.query(cls).filter(cls.id == payment_id).first()
        if not payment:
            raise ValueError("Payment not found")
        payment.status = status
        db.commit()
        db.refresh(payment)
        return payment