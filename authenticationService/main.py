import re
import warnings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.auth import router as auth_router
from app.routes.customer import router as customer_router
from app.routes.driver import router as driver_router
from app.routes.vehicle import router as vehicle_router


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
]

app.add_middleware(
    RegexCORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(customer_router, prefix="/customer", tags=["customer"])
app.include_router(driver_router, prefix="/driver", tags=["driver"])
app.include_router(vehicle_router, prefix="/vehicle", tags=["vehicle"])