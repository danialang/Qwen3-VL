import secrets
from datetime import timedelta

from sqlalchemy import and_
from sqlalchemy.orm import Session

from .config import settings
from .models import Receipt, Reservation, ReservationStatus, RoomType, SecurityCode, User, UserRole
from .receipts import generate_receipt_pdf

SUGGESTION_WINDOW_DAYS = 30


class ReservationConflictError(Exception):
    """Créneau indisponible : conflit avec un événement existant."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def overlap_filter(room: RoomType, event_date, start_time, end_time):
    return and_(
        Reservation.room == room,
        Reservation.event_date == event_date,
        Reservation.status != ReservationStatus.cancelled,
        Reservation.start_time < end_time,
        Reservation.end_time > start_time,
    )


def find_conflict(db: Session, room: RoomType, event_date, start_time, end_time) -> Reservation | None:
    return db.query(Reservation).filter(overlap_filter(room, event_date, start_time, end_time)).first()


def suggest_next_available(db: Session, room: RoomType, start_time, end_time, from_date):
    for offset in range(1, SUGGESTION_WINDOW_DAYS + 1):
        candidate = from_date + timedelta(days=offset)
        if not find_conflict(db, room, candidate, start_time, end_time):
            return candidate
    return None


def generate_security_code() -> str:
    return secrets.token_hex(4).upper()


def create_reservation(db: Session, user: User, room: RoomType, event_date, start_time, end_time) -> Reservation:
    """Crée une réservation en appliquant la priorité du Collège (source unique de vérité,
    utilisée à la fois par l'API REST et par l'assistant IA)."""
    conflict = find_conflict(db, room, event_date, start_time, end_time)
    if conflict:
        suggestion = suggest_next_available(db, room, start_time, end_time, event_date)
        reason = "un événement du Collège" if conflict.is_internal else "une autre réservation"
        detail = f"Créneau indisponible ({reason})."
        if suggestion:
            detail += f" Prochaine date disponible : {suggestion.isoformat()}."
        raise ReservationConflictError(detail)

    is_internal = user.role in (UserRole.admin, UserRole.dev)
    reservation = Reservation(
        user_id=user.id,
        room=room,
        event_date=event_date,
        start_time=start_time,
        end_time=end_time,
        accepted_rules=True,
        is_internal=is_internal,
        amount=0 if is_internal else settings.RESERVATION_AMOUNT,
        status=ReservationStatus.validated if is_internal else ReservationStatus.pending,
    )
    db.add(reservation)
    db.commit()
    db.refresh(reservation)

    code = SecurityCode(reservation_id=reservation.id, code=generate_security_code())
    db.add(code)
    db.commit()
    db.refresh(reservation)

    if reservation.status == ReservationStatus.validated:
        pdf_path = generate_receipt_pdf(reservation, code.code, user)
        db.add(Receipt(reservation_id=reservation.id, pdf_path=pdf_path))
        db.commit()
        db.refresh(reservation)

    return reservation
