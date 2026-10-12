from datetime import date, datetime, time
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field, field_validator

from .models import ReservationStatus, RoomType, UserRole
from .tariffs import DEFAULT_CATEGORY, MAX_EXTRA_QUANTITY


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


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: str
    new_password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ExtraSelection(BaseModel):
    key: str
    quantity: int = Field(ge=1, le=MAX_EXTRA_QUANTITY)


class ReservationCreate(BaseModel):
    room: RoomType
    event_date: date
    start_time: time
    end_time: time
    accepted_rules: bool
    client_category: str = DEFAULT_CATEGORY
    extras: list[ExtraSelection] = []

    @field_validator("end_time")
    @classmethod
    def check_times(cls, v, info):
        start = info.data.get("start_time")
        if start and v <= start:
            raise ValueError("L'heure de fin doit être après l'heure de début.")
        return v


class QuoteRequest(BaseModel):
    room: RoomType
    start_time: time
    end_time: time
    client_category: str = DEFAULT_CATEGORY
    extras: list[ExtraSelection] = []


class QuoteLineOut(BaseModel):
    key: str
    label: str
    quantity: int
    unit_price: int
    total: int


class QuoteOut(BaseModel):
    room: RoomType
    client_category: str
    client_category_label: str
    duration_type: str
    duration_label: str
    rental: int
    extras: list[QuoteLineOut]
    extras_total: int
    total: int
    deposit: int
    total_due: int


class ReservationOut(BaseModel):
    id: int
    room: RoomType
    event_date: date
    start_time: time
    end_time: time
    status: ReservationStatus
    amount: Decimal
    deposit: Decimal = Decimal(0)
    total_due: Decimal = Decimal(0)
    client_category: str | None = None
    client_category_label: str | None = None
    duration_type: str | None = None
    duration_label: str | None = None
    extras: list[QuoteLineOut] = []
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


class AdminOverviewOut(BaseModel):
    year: int
    month: int
    reservations_this_month: int
    revenue_this_month_fcfa: float
    revenue_upcoming_fcfa: float
    revenue_year_fcfa: float
    revenue_by_month: list[float]
    pending_reservations_count: int
    occupancy_rate_this_month_percent: dict[str, float]
