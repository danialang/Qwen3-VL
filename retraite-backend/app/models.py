import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Time,
)
from sqlalchemy.orm import relationship

from .database import Base


class UserRole(str, enum.Enum):
    dev = "dev"
    admin = "admin"
    client = "client"


class RoomType(str, enum.Enum):
    gymnase = "gymnase"
    salle_fetes = "salle_fetes"


class ReservationStatus(str, enum.Enum):
    pending = "pending"
    validated = "validated"
    cancelled = "cancelled"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(30))
    role = Column(Enum(UserRole), default=UserRole.client, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    reservations = relationship("Reservation", back_populates="user")


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    room = Column(Enum(RoomType), nullable=False)
    event_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    status = Column(Enum(ReservationStatus), default=ReservationStatus.pending, nullable=False)
    amount = Column(Numeric(12, 2), default=0, nullable=False)
    is_internal = Column(Boolean, default=False, nullable=False)
    accepted_rules = Column(Boolean, default=False, nullable=False)
    payment_method = Column(String(50), nullable=True)
    payment_reference = Column(String(255), nullable=True)
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="reservations")
    security_code = relationship("SecurityCode", back_populates="reservation", uselist=False)
    receipt = relationship("Receipt", back_populates="reservation", uselist=False)


class SecurityCode(Base):
    __tablename__ = "security_codes"

    id = Column(Integer, primary_key=True)
    reservation_id = Column(Integer, ForeignKey("reservations.id"), unique=True, nullable=False)
    code = Column(String(64), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    reservation = relationship("Reservation", back_populates="security_code")


class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True)
    reservation_id = Column(Integer, ForeignKey("reservations.id"), unique=True, nullable=False)
    pdf_path = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    reservation = relationship("Reservation", back_populates="receipt")
