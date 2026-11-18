
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, EmailStr


# ==================================
# USER SCHEMAS
# ==================================

class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8)


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

    model_config = ConfigDict(from_attributes=True)


# ==================================
# AUTHENTICATION SCHEMAS
# ==================================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ==================================
# EVENT SCHEMAS
# ==================================

class EventCreate(BaseModel):
    title: str = Field(min_length=3, max_length=150)
    description: str | None = None
    event_date: datetime
    location: str = Field(min_length=2, max_length=200)
    capacity: int = Field(gt=0)


class EventUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=150)
    description: str | None = None
    event_date: datetime | None = None
    location: str | None = Field(default=None, min_length=2, max_length=200)
    capacity: int | None = Field(default=None, gt=0)


class EventResponse(BaseModel):
    id: int
    title: str
    description: str | None
    event_date: datetime
    location: str
    capacity: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==================================
# REGISTRATION SCHEMAS
# ==================================

class RegistrationCreate(BaseModel):
    user_id: int = Field(gt=0)


class RegistrationResponse(BaseModel):
    id: int
    user_id: int
    event_id: int
    registered_at: datetime

    model_config = ConfigDict(from_attributes=True)
