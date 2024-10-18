from typing import Optional
from pydantic import BaseModel, EmailStr, Field

from app.utils.enums import GenderEnum


class Location(BaseModel):
    latitude: float
    longitude: float


class RegisterCustomerRequest(BaseModel):
    phone_number: str = Field(..., min_length=10, max_length=15, pattern=r'^\+?[0-9]+$')
    password: str
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    gender: GenderEnum
    home_location: Optional[Location] = None
    home_address: Optional[str] = None


class LoginCustomerRequest(BaseModel):
    phone_number: str = Field(..., min_length=10, max_length=15, pattern=r'^\+?[0-9]+$')
    password: str


class RegisterLoginCustomerResponse(BaseModel):
    message: str
    access_token: str