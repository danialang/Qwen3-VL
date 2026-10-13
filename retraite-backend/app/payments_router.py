import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .models import Reservation
from .payments import PaymentProviderError, available_methods, get_provider
from .schemas import PaymentOptionsOut

router = APIRouter(prefix="/payments", tags=["payments"])
logger = logging.getLogger("retraite.payments")


def offered_methods() -> list[dict]:
    """Le virement n'est proposé que si les coordonnées bancaires sont renseignées."""
    return [m for m in available_methods() if m["key"] != "virement" or settings.BANK_TRANSFER_DETAILS]


@router.get("/options", response_model=PaymentOptionsOut)
def payment_options():
    return PaymentOptionsOut(
        methods=offered_methods(),
        instructions=settings.PAYMENT_INSTRUCTIONS,
        bank_details=settings.BANK_TRANSFER_DETAILS,
    )


@router.post("/webhook/{provider_key}")
async def payment_webhook(provider_key: str, request: Request, db: Session = Depends(get_db)):
    """Confirmation envoyée par l'opérateur. Seule source de vérité pour un paiement en ligne."""
    provider = get_provider(provider_key)
    if not provider or not provider.configured:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Opérateur inconnu.")
    try:
        result = provider.parse_webhook(await request.body(), dict(request.headers))
    except PaymentProviderError as e:
        logger.warning("Webhook %s refusé : %s", provider_key, e)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Notification invalide.")

    r = db.query(Reservation).filter(
        Reservation.payment_method == provider_key, Reservation.payment_reference == result.transaction_id
    ).first()
    if not r:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Transaction inconnue.")
    if result.success and not r.paid_at:
        r.paid_at = datetime.utcnow()
        db.commit()
        logger.info("Paiement %s confirmé pour réservation #%s", provider_key, r.id)
    return {"ok": True}
