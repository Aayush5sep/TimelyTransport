import re
import warnings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from sqs import consume_sqs_messages
from app.config import settings
from app.routes.booking import router as booking_router
from app.routes.payment import router as payment_router
from app.routes.rating import router as rating_router


# Ignore Deprecation Warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

app = FastAPI()

class RegexCORSMiddleware(CORSMiddleware):
    def is_allowed_origin(self, origin: str) -> bool:
        for pattern in self.allow_origins:
            if re.fullmatch(pattern, origin):
                return True
        return False

allowed_origins = [
    "*",
    "http://localhost:8000",
]

app.add_middleware(
    RegexCORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(booking_router, prefix="/bookings", tags=["Bookings"])
app.include_router(rating_router, prefix="/ratings", tags=["Ratings"])
app.include_router(payment_router, prefix="/payments", tags=["Payments"])


@app.on_event("startup")
async def start_background_tasks():
    """
    Start the SQS consumer concurrently with the FastAPI app on startup.
    """
    print("Starting SQS consumer...")
    # Create the SQS consumer as an async background task
    asyncio.create_task(consume_sqs_messages())


@app.get("/")
async def root():
    return {"message": "Trip Management Service is running"}