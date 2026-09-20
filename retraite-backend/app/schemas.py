from datetime import date, datetime, time
from decimal import Decimal

from pydantic import BaseModel, EmailStr, field_validator

from .models import ReservationStatus, RoomType, UserRole


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: str | None = None


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    phone: str | None
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ReservationCreate(BaseModel):
    room: RoomType
    event_date: date
    start_time: time
    end_time: time
    accepted_rules: bool

    @field_validator("end_time")
    @classmethod
    def check_times(cls, v, info):
        start = info.data.get("start_time")
        if start and v <= start:
            raise ValueError("L'heure de fin doit être après l'heure de début.")
        return v


class ReservationOut(BaseModel):
    id: int
    room: RoomType
    event_date: date
    start_time: time
    end_time: time
    status: ReservationStatus
    amount: Decimal
    is_internal: bool
    user_id: int
    security_code: str | None = None
    payment_method: str | None = None
    payment_reference: str | None = None
    paid_at: datetime | None = None
    has_receipt: bool = False
    created_at: datetime


class AvailabilityOut(BaseModel):
    room: RoomType
    event_date: date
    start_time: time
    end_time: time
    is_internal: bool
    status: ReservationStatus


PAYMENT_METHODS = ("paysika_orange_money", "paysika_mtn_momo", "paypal_sandbox")


class PaymentCreate(BaseModel):
    method: str
    reference: str

    @field_validator("method")
    @classmethod
    def check_method(cls, v):
        if v not in PAYMENT_METHODS:
            raise ValueError(f"Méthode de paiement invalide. Attendu : {', '.join(PAYMENT_METHODS)}.")
        return v
