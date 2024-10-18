from fastapi import APIRouter, Depends, HTTPException, Request

from app.schemas.payment import PaymentCreate, PaymentResponse
from app.models.payment import Payment
from app.models.booking import Booking
from app.database import DBFactory


router = APIRouter()


@router.post("/", response_model=PaymentResponse)
async def initiate_payment(payment: PaymentCreate):
    try:
        with DBFactory() as db:
            new_payment = Payment.create_payment(db, payment)
            # Call to third-party payment gateway
            return new_payment
    
    except Exception as err:
        raise err


@router.post("/webhook")
async def payment_webhook(request: Request):
    """
    Webhook endpoint to handle payment status updates.
    """
    try:
        with DBFactory() as db:
            payload = await request.json()

            payment_id = payload.get("payment_id")
            status = payload.get("status")  # Example: 'SUCCESS' or 'FAILED'

            if not payment_id or not status:
                raise HTTPException(status_code=400, detail="Invalid payload")

            # Update the payment status in the database
            payment = Payment.update_payment_status(db, payment_id, status)

            # If payment is successful, update the booking status
            if status == "SUCCESS":
                Booking.update_booking_status(db, payment.trip_id, "ACCEPTED")
            else:
                Booking.update_booking_status(db, payment.trip_id, "CANCELLED")

            # TODO: Notify driver & customer of payment

            return {"message": "Payment status updated"}
        
    except Exception as err:
        raise err