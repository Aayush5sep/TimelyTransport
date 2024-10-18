from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import date

from app.utils.enums import GenderEnum


class RegisterDriverRequest(BaseModel):
    phone_number: str = Field(..., min_length=10, max_length=15, pattern=r'^\+?[0-9]+$')
    password: str
    name: str
    email: Optional[EmailStr] = None
    gender: GenderEnum
    dob: date


class LoginDriverRequest(BaseModel):
    phone_number: str = Field(..., min_length=10, max_length=15, pattern=r'^\+?[0-9]+$')
    password: str


class RegisterLoginDriverResponse(BaseModel):
    message: str
    access_token: str