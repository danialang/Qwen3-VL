from datetime import datetime

from sqlalchemy import extract
from sqlalchemy.orm import Session

from .models import Reservation, ReservationStatus, RoomType


def reservations_this_month(db: Session, now: datetime | None = None) -> int:
    now = now or datetime.utcnow()
    return (
        db.query(Reservation)
        .filter(
            extract("year", Reservation.event_date) == now.year,
            extract("month", Reservation.event_date) == now.month,
        )
        .count()
    )


def pending_reservations(db: Session) -> list[Reservation]:
    return (
        db.query(Reservation)
        .filter(Reservation.status == ReservationStatus.pending)
        .order_by(Reservation.event_date)
        .all()
    )


def _is_leap_year(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def annual_report(db: Session, year: int) -> dict:
    reservations = db.query(Reservation).filter(extract("year", Reservation.event_date) == year).all()

    by_room = {room.value: 0 for room in RoomType}
    by_status = {status.value: 0 for status in ReservationStatus}
    days_booked: dict[str, set] = {room.value: set() for room in RoomType}
    revenue = 0.0
    internal_count = 0

    for r in reservations:
        by_room[r.room.value] += 1
        by_status[r.status.value] += 1
        if r.is_internal:
            internal_count += 1
        if r.status == ReservationStatus.validated:
            revenue += float(r.amount)
        if r.status != ReservationStatus.cancelled:
            days_booked[r.room.value].add(r.event_date)

    days_in_year = 366 if _is_leap_year(year) else 365
    occupancy_rate_percent = {
        room: round(len(days) / days_in_year * 100, 1) for room, days in days_booked.items()
    }

    return {
        "year": year,
        "total_reservations": len(reservations),
        "reservations_by_room": by_room,
        "reservations_by_status": by_status,
        "internal_reservations_count": internal_count,
        "external_reservations_count": len(reservations) - internal_count,
        "total_revenue_fcfa": revenue,
        "occupancy_rate_percent": occupancy_rate_percent,
    }
