import json
import logging
import os
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from .database import get_db
from .models import Receipt, Reservation, ReservationStatus, RoomType, User, UserRole
from .receipts import generate_receipt_pdf
from .reservation_logic import (
    ReservationConflictError,
    create_reservation as create_reservation_record,
    quote_for,
)
from .schemas import AvailabilityOut, PaymentCreate, QuoteLineOut, QuoteOut, QuoteRequest, ReservationCreate, ReservationOut
from .tariffs import DURATION_LABELS, TariffError, category_label, venue_rooms
from .security import get_current_user, require_roles

router = APIRouter(prefix="/reservations", tags=["reservations"])
logger = logging.getLogger("retraite.reservations")


def _extras_of(r: Reservation) -> list[QuoteLineOut]:
    return [QuoteLineOut(**line) for line in json.loads(r.extras_json)] if r.extras_json else []


def _to_out(r: Reservation) -> ReservationOut:
    deposit = r.deposit or 0
    return ReservationOut(
        id=r.id,
        room=r.room,
        event_date=r.event_date,
        start_time=r.start_time,
        end_time=r.end_time,
        status=r.status,
        amount=r.amount,
        deposit=deposit,
        total_due=r.amount + deposit,
        client_category=r.client_category,
        client_category_label=category_label(r.client_category) if r.client_category else None,
        duration_type=r.duration_type,
        duration_label=DURATION_LABELS.get(r.duration_type) if r.duration_type else None,
        extras=_extras_of(r),
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

    try:
        reservation = create_reservation_record(
            db,
            current_user,
            payload.room,
            payload.event_date,
            payload.start_time,
            payload.end_time,
            client_category=payload.client_category,
            extras={e.key: e.quantity for e in payload.extras},
        )
    except TariffError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    except ReservationConflictError as e:
        logger.info(
            "Conflit de réservation refusé pour user_id=%s room=%s date=%s : %s",
            current_user.id, payload.room.value, payload.event_date, e.message,
        )
        raise HTTPException(status.HTTP_409_CONFLICT, e.message)

    logger.info(
        "Réservation #%s créée par user_id=%s room=%s date=%s statut=%s",
        reservation.id, current_user.id, reservation.room.value, reservation.event_date, reservation.status.value,
    )
    return _to_out(reservation)


@router.post("/quote", response_model=QuoteOut)
def get_quote(payload: QuoteRequest, current_user: User = Depends(get_current_user)):
    """Prix d'une location avant de réserver : l'application l'affiche en direct à chaque choix du client."""
    try:
        quote = quote_for(
            payload.room,
            payload.client_category,
            payload.start_time,
            payload.end_time,
            {e.key: e.quantity for e in payload.extras},
        )
    except TariffError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    return QuoteOut(
        room=payload.room,
        client_category=quote.category,
        client_category_label=category_label(quote.category),
        duration_type=quote.duration_type,
        duration_label=DURATION_LABELS[quote.duration_type],
        rental=quote.rental,
        extras=[QuoteLineOut(**vars(line)) for line in quote.extras],
        extras_total=quote.extras_total,
        total=quote.total,
        deposit=quote.deposit,
        total_due=quote.total_due,
    )


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
        # Le calendrier d'un espace montre aussi les créneaux pris par les offres du même lieu.
        query = query.filter(Reservation.room.in_([RoomType(r) for r in venue_rooms(room.value)]))
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
    logger.info("Paiement test enregistré pour réservation #%s méthode=%s", r.id, payload.method)
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
    logger.info("Réservation #%s validée par admin_id=%s", r.id, current_user.id)
    return _to_out(r)


@router.post("/{reservation_id}/cancel", response_model=ReservationOut)
def cancel_reservation(reservation_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    r = _get_owned_reservation(db, reservation_id, current_user)
    r.status = ReservationStatus.cancelled
    db.commit()
    db.refresh(r)
    logger.info("Réservation #%s annulée par user_id=%s", r.id, current_user.id)
    return _to_out(r)


@router.get("/{reservation_id}/receipt")
def download_receipt(reservation_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    r = _get_owned_reservation(db, reservation_id, current_user)
    if not r.receipt:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Reçu non disponible.")
    if not os.path.exists(r.receipt.pdf_path):
        # Le disque de l'hébergeur est temporaire : on refabrique le PDF s'il a disparu.
        r.receipt.pdf_path = generate_receipt_pdf(r, r.security_code.code, r.user)
        db.commit()
    return FileResponse(r.receipt.pdf_path, media_type="application/pdf", filename=f"recu_{r.id}.pdf")
