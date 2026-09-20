import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy import and_
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .models import Receipt, Reservation, ReservationStatus, RoomType, SecurityCode, User, UserRole
from .receipts import generate_receipt_pdf
from .schemas import AvailabilityOut, PaymentCreate, ReservationCreate, ReservationOut
from .security import get_current_user, require_roles

router = APIRouter(prefix="/reservations", tags=["reservations"])

SUGGESTION_WINDOW_DAYS = 30


def _overlap_filter(room, event_date, start_time, end_time):
    return and_(
        Reservation.room == room,
        Reservation.event_date == event_date,
        Reservation.status != ReservationStatus.cancelled,
        Reservation.start_time < end_time,
        Reservation.end_time > start_time,
    )


def _find_conflict(db: Session, room, event_date, start_time, end_time):
    return db.query(Reservation).filter(_overlap_filter(room, event_date, start_time, end_time)).first()


def _suggest_next_available(db: Session, room, start_time, end_time, from_date):
    for offset in range(1, SUGGESTION_WINDOW_DAYS + 1):
        candidate = from_date + timedelta(days=offset)
        if not _find_conflict(db, room, candidate, start_time, end_time):
            return candidate
    return None


def _generate_security_code() -> str:
    return secrets.token_hex(4).upper()


def _to_out(r: Reservation) -> ReservationOut:
    return ReservationOut(
        id=r.id,
        room=r.room,
        event_date=r.event_date,
        start_time=r.start_time,
        end_time=r.end_time,
        status=r.status,
        amount=r.amount,
        is_internal=r.is_internal,
        user_id=r.user_id,
        security_code=r.security_code.code if r.security_code else None,
        payment_method=r.payment_method,
        payment_reference=r.payment_reference,
        paid_at=r.paid_at,
        has_receipt=r.receipt is not None,
        created_at=r.created_at,
    )


def _get_owned_reservation(db: Session, reservation_id: int, current_user: User) -> Reservation:
    r = db.get(Reservation, reservation_id)
    if not r or (current_user.role == UserRole.client and r.user_id != current_user.id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Réservation introuvable.")
    return r


@router.post("", response_model=ReservationOut, status_code=status.HTTP_201_CREATED)
def create_reservation(
    payload: ReservationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not payload.accepted_rules:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Vous devez accepter le règlement intérieur.")

    is_internal = current_user.role in (UserRole.admin, UserRole.dev)

    conflict = _find_conflict(db, payload.room, payload.event_date, payload.start_time, payload.end_time)
    if conflict:
        suggestion = _suggest_next_available(db, payload.room, payload.start_time, payload.end_time, payload.event_date)
        reason = "un événement du Collège" if conflict.is_internal else "une autre réservation"
        detail = f"Créneau indisponible ({reason})."
        if suggestion:
            detail += f" Prochaine date disponible : {suggestion.isoformat()}."
        raise HTTPException(status.HTTP_409_CONFLICT, detail)

    reservation = Reservation(
        user_id=current_user.id,
        room=payload.room,
        event_date=payload.event_date,
        start_time=payload.start_time,
        end_time=payload.end_time,
        accepted_rules=True,
        is_internal=is_internal,
        amount=0 if is_internal else settings.RESERVATION_AMOUNT,
        status=ReservationStatus.validated if is_internal else ReservationStatus.pending,
    )
    db.add(reservation)
    db.commit()
    db.refresh(reservation)

    code = SecurityCode(reservation_id=reservation.id, code=_generate_security_code())
    db.add(code)
    db.commit()
    db.refresh(reservation)

    if reservation.status == ReservationStatus.validated:
        pdf_path = generate_receipt_pdf(reservation, code.code, current_user)
        db.add(Receipt(reservation_id=reservation.id, pdf_path=pdf_path))
        db.commit()
        db.refresh(reservation)

    return _to_out(reservation)


@router.get("", response_model=list[ReservationOut])
def list_reservations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Reservation)
    if current_user.role == UserRole.client:
        query = query.filter(Reservation.user_id == current_user.id)
    return [_to_out(r) for r in query.order_by(Reservation.event_date.desc()).all()]


@router.get("/availability", response_model=list[AvailabilityOut])
def get_availability(
    room: RoomType | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Créneaux occupés (sans données personnelles) pour construire le calendrier client."""
    query = db.query(Reservation).filter(Reservation.status != ReservationStatus.cancelled)
    if room:
        query = query.filter(Reservation.room == room)
    return query.order_by(Reservation.event_date).all()


@router.get("/{reservation_id}", response_model=ReservationOut)
def get_reservation(reservation_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return _to_out(_get_owned_reservation(db, reservation_id, current_user))


@router.post("/{reservation_id}/pay", response_model=ReservationOut)
def pay_reservation(
    reservation_id: int,
    payload: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    r = _get_owned_reservation(db, reservation_id, current_user)
    if r.is_internal:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Réservation interne au Collège : aucun paiement requis.")
    if r.status == ReservationStatus.cancelled:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Réservation annulée.")

    r.payment_method = payload.method
    r.payment_reference = payload.reference
    r.paid_at = datetime.utcnow()
    db.commit()
    db.refresh(r)
    return _to_out(r)


@router.post("/{reservation_id}/validate", response_model=ReservationOut)
def validate_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.dev)),
):
    r = db.get(Reservation, reservation_id)
    if not r:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Réservation introuvable.")
    if r.status == ReservationStatus.cancelled:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Réservation annulée, validation impossible.")

    r.status = ReservationStatus.validated
    db.commit()

    if not r.receipt:
        pdf_path = generate_receipt_pdf(r, r.security_code.code, r.user)
        db.add(Receipt(reservation_id=r.id, pdf_path=pdf_path))
        db.commit()

    db.refresh(r)
    return _to_out(r)


@router.post("/{reservation_id}/cancel", response_model=ReservationOut)
def cancel_reservation(reservation_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    r = _get_owned_reservation(db, reservation_id, current_user)
    r.status = ReservationStatus.cancelled
    db.commit()
    db.refresh(r)
    return _to_out(r)


@router.get("/{reservation_id}/receipt")
def download_receipt(reservation_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    r = _get_owned_reservation(db, reservation_id, current_user)
    if not r.receipt:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Reçu non disponible.")
    return FileResponse(r.receipt.pdf_path, media_type="application/pdf", filename=f"recu_{r.id}.pdf")
