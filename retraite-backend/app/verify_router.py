import html
import logging

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from .database import get_db
from .models import Reservation, ReservationStatus
from .receipts import ROOM_LABELS
from .verification import is_valid_token

router = APIRouter(tags=["verification"])
logger = logging.getLogger("retraite.verify")

STATUS_LABELS = {
    ReservationStatus.pending: "En attente de validation",
    ReservationStatus.validated: "Validée",
    ReservationStatus.cancelled: "Annulée",
}

PAGE = """<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Vérification de reçu</title>
<style>
body{{font-family:Arial,sans-serif;background:#f3f4f6;margin:0;padding:24px;color:#1f2937}}
.card{{max-width:420px;margin:0 auto;background:#fff;border-radius:14px;padding:24px;box-shadow:0 2px 10px #0002}}
.badge{{display:inline-block;padding:8px 14px;border-radius:999px;font-weight:bold;color:#fff;background:{color}}}
td{{padding:6px 0;vertical-align:top}} td:first-child{{color:#6b7280;padding-right:14px}}
h1{{font-size:18px;margin:0 0 4px}} small{{color:#6b7280}}
</style></head><body><div class="card">
<h1>Collège Catholique Bilingue de la Retraite</h1><small>Vérification d'un reçu de réservation</small>
<p><span class="badge">{title}</span></p>{body}
</div></body></html>"""


def _mask(name: str) -> str:
    return " ".join(part[0] + "***" for part in name.split() if part)


def _page(title: str, color: str, body: str, status_code: int = 200) -> HTMLResponse:
    return HTMLResponse(PAGE.format(title=html.escape(title), color=color, body=body), status_code=status_code)


@router.get("/verify/{reservation_id}/{token}", response_class=HTMLResponse)
def verify_receipt(reservation_id: int, token: str, db: Session = Depends(get_db)):
    r = db.get(Reservation, reservation_id)
    if not r or not r.security_code or not is_valid_token(reservation_id, r.security_code.code, token):
        logger.warning("Vérification de reçu refusée (reçu n°%s)", reservation_id)
        return _page(
            "REÇU NON AUTHENTIQUE",
            "#b91c1c",
            "<p>Ce reçu ne correspond à aucune réservation enregistrée. Ne l'acceptez pas.</p>",
            status_code=404,
        )

    if r.status == ReservationStatus.validated:
        title, color = "REÇU AUTHENTIQUE", "#15803d"
    elif r.status == ReservationStatus.cancelled:
        title, color = "RÉSERVATION ANNULÉE", "#b91c1c"
    else:
        title, color = "RÉSERVATION NON VALIDÉE", "#b45309"

    rows = [
        ("Réservation n°", str(r.id)),
        ("Salle", ROOM_LABELS[r.room.value]),
        ("Date", r.event_date.strftime("%d/%m/%Y")),
        ("Horaire", f"{r.start_time.strftime('%H:%M')} - {r.end_time.strftime('%H:%M')}"),
        ("Statut", STATUS_LABELS[r.status]),
        ("Client", _mask(r.user.full_name)),
    ]
    body = "<table>" + "".join(f"<tr><td>{html.escape(k)}</td><td>{html.escape(v)}</td></tr>" for k, v in rows) + "</table>"
    logger.info("Reçu n°%s vérifié : %s", r.id, title)
    return _page(title, color, body)
