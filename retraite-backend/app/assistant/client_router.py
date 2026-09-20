import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import Reservation, RoomType, User
from ..reservation_logic import ReservationConflictError, create_reservation, find_conflict, suggest_next_available
from ..security import get_current_user
from .common import get_anthropic_client, parse_date, parse_time, run_tool_loop, tool_error, tool_ok

router = APIRouter(prefix="/assistant/client", tags=["assistant"])
logger = logging.getLogger("retraite.assistant.client")

SYSTEM_PROMPT = (
    "Tu es l'assistant de réservation du Collège Catholique Bilingue de la Retraite. "
    "Tu aides un client à réserver le Gymnase ou la Salle des fêtes. "
    f"Le montant est fixe : {settings.RESERVATION_AMOUNT:.0f} FCFA (0 FCFA pour une réservation "
    "interne du Collège, cas rare côté client). "
    "Avant toute réservation, vérifie la disponibilité avec check_availability. "
    "N'appelle create_reservation qu'après avoir obtenu une confirmation explicite de "
    "l'utilisateur qu'il a lu et accepte le règlement intérieur du Collège (accepted_rules=true). "
    "Si le créneau est indisponible, propose la date suggérée par l'outil. "
    "Une fois la réservation créée, communique clairement son statut (en attente de validation "
    "par l'administration, sauf réservation interne) et le code de sécurité. "
    "Réponds toujours en français, de façon concise et chaleureuse."
)

TOOLS = [
    {
        "name": "check_availability",
        "description": "Vérifie si un créneau est disponible pour une salle donnée avant de proposer une réservation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "room": {"type": "string", "enum": ["gymnase", "salle_fetes"]},
                "event_date": {"type": "string", "description": "Date au format AAAA-MM-JJ"},
                "start_time": {"type": "string", "description": "Heure de début au format HH:MM"},
                "end_time": {"type": "string", "description": "Heure de fin au format HH:MM"},
            },
            "required": ["room", "event_date", "start_time", "end_time"],
        },
    },
    {
        "name": "create_reservation",
        "description": (
            "Crée une réservation pour l'utilisateur connecté. N'appelle cet outil qu'après avoir "
            "vérifié la disponibilité ET obtenu la confirmation explicite de l'utilisateur qu'il "
            "accepte le règlement intérieur du Collège (accepted_rules doit être true)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "room": {"type": "string", "enum": ["gymnase", "salle_fetes"]},
                "event_date": {"type": "string", "description": "Date au format AAAA-MM-JJ"},
                "start_time": {"type": "string", "description": "Heure de début au format HH:MM"},
                "end_time": {"type": "string", "description": "Heure de fin au format HH:MM"},
                "accepted_rules": {"type": "boolean"},
            },
            "required": ["room", "event_date", "start_time", "end_time", "accepted_rules"],
        },
    },
    {
        "name": "list_my_reservations",
        "description": "Liste les réservations de l'utilisateur connecté, avec leur statut et code de sécurité.",
        "input_schema": {"type": "object", "properties": {}},
    },
]


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    reply: str
    history: list[ChatMessage]


def _make_executor(db: Session, user: User):
    def executor(name: str, tool_input: dict) -> tuple[str, bool]:
        try:
            if name == "check_availability":
                room = RoomType(tool_input["room"])
                event_date = parse_date(tool_input["event_date"])
                start_time = parse_time(tool_input["start_time"])
                end_time = parse_time(tool_input["end_time"])
                conflict = find_conflict(db, room, event_date, start_time, end_time)
                if not conflict:
                    return tool_ok({"available": True})
                suggestion = suggest_next_available(db, room, start_time, end_time, event_date)
                return tool_ok({
                    "available": False,
                    "reason": "événement du Collège" if conflict.is_internal else "autre réservation",
                    "suggested_date": suggestion.isoformat() if suggestion else None,
                })

            if name == "create_reservation":
                room = RoomType(tool_input["room"])
                event_date = parse_date(tool_input["event_date"])
                start_time = parse_time(tool_input["start_time"])
                end_time = parse_time(tool_input["end_time"])
                if not tool_input.get("accepted_rules"):
                    return tool_ok({
                        "success": False,
                        "reason": "L'utilisateur doit d'abord confirmer qu'il accepte le règlement intérieur.",
                    })
                try:
                    reservation = create_reservation(db, user, room, event_date, start_time, end_time)
                except ReservationConflictError as e:
                    return tool_ok({"success": False, "reason": e.message})
                logger.info(
                    "Réservation #%s créée via assistant IA pour user_id=%s", reservation.id, user.id
                )
                return tool_ok({
                    "success": True,
                    "reservation_id": reservation.id,
                    "status": reservation.status.value,
                    "amount": float(reservation.amount),
                    "is_internal": reservation.is_internal,
                    "security_code": reservation.security_code.code if reservation.security_code else None,
                })

            if name == "list_my_reservations":
                reservations = (
                    db.query(Reservation)
                    .filter(Reservation.user_id == user.id)
                    .order_by(Reservation.event_date.desc())
                    .all()
                )
                return tool_ok({
                    "reservations": [
                        {
                            "id": r.id,
                            "room": r.room.value,
                            "event_date": r.event_date.isoformat(),
                            "status": r.status.value,
                            "amount": float(r.amount),
                            "security_code": r.security_code.code if r.security_code else None,
                        }
                        for r in reservations
                    ]
                })

            return tool_error(f"Outil inconnu : {name}")
        except (KeyError, ValueError) as e:
            return tool_error(f"Paramètres invalides : {e}")

    return executor


@router.post("", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    client = get_anthropic_client()
    messages = [{"role": m.role, "content": m.content} for m in payload.history]
    messages.append({"role": "user", "content": payload.message})

    reply = run_tool_loop(client, SYSTEM_PROMPT, TOOLS, messages, _make_executor(db, current_user))

    new_history = payload.history + [
        ChatMessage(role="user", content=payload.message),
        ChatMessage(role="assistant", content=reply),
    ]
    return ChatResponse(reply=reply, history=new_history)
