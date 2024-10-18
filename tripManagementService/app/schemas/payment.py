from pydantic import BaseModel
from app.utils.enums import PaymentMode, PaymentStatus


class PaymentCreate(BaseModel):
    trip_id: str
    amount: float
    mode: PaymentMode

class PaymentResponse(BaseModel):
    id: str
    status: PaymentStatus
    amount: float