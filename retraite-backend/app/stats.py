import calendar
from datetime import date, datetime

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


def monthly_overview(db: Session, now: datetime | None = None) -> dict:
    """Chiffres clés du mois en cours, pour les cartes de statistiques du tableau de bord admin."""
    now = now or datetime.utcnow()
    year, month = now.year, now.month

    year_reservations = db.query(Reservation).filter(extract("year", Reservation.event_date) == year).all()
    reservations = [r for r in year_reservations if r.event_date.month == month]

    # Revenus : uniquement les réservations validées (l'argent est compté après validation).
    revenue = sum(float(r.amount) for r in reservations if r.status == ReservationStatus.validated)
    revenue_by_month = [0.0] * 12
    for r in year_reservations:
        if r.status == ReservationStatus.validated:
            revenue_by_month[r.event_date.month - 1] += float(r.amount)

    days_in_month = calendar.monthrange(year, month)[1]
    end_of_month = date(year, month, days_in_month)
    upcoming = (
        db.query(Reservation)
        .filter(Reservation.status == ReservationStatus.validated, Reservation.event_date > end_of_month)
        .all()
    )
    revenue_upcoming = sum(float(r.amount) for r in upcoming)

    days_booked: dict[str, set] = {room.value: set() for room in RoomType}
    for r in reservations:
        if r.status != ReservationStatus.cancelled:
            days_booked[r.room.value].add(r.event_date)

    occupancy_rate_percent = {
        room: round(len(days) / days_in_month * 100, 1) for room, days in days_booked.items()
    }

    pending_count = db.query(Reservation).filter(Reservation.status == ReservationStatus.pending).count()

    return {
        "year": year,
        "month": month,
        "reservations_this_month": len(reservations),
        "revenue_this_month_fcfa": revenue,
        "revenue_upcoming_fcfa": revenue_upcoming,
        "revenue_year_fcfa": sum(revenue_by_month),
        "revenue_by_month": revenue_by_month,
        "pending_reservations_count": pending_count,
        "occupancy_rate_this_month_percent": occupancy_rate_percent,
    }
