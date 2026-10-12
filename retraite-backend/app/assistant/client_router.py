import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Reservation, RoomType, User
from ..reservation_logic import (
    ReservationConflictError,
    create_reservation,
    find_conflict,
    quote_for,
    suggest_next_available,
)
from ..security import get_current_user
from ..tariffs import CATEGORY_LABELS, DEFAULT_CATEGORY, EXTRAS, SPACES, TariffError, category_label, room_label
from .common import get_anthropic_client, parse_date, parse_time, run_tool_loop, tool_error, tool_ok

router = APIRouter(prefix="/assistant/client", tags=["assistant"])
logger = logging.getLogger("retraite.assistant.client")

_SPACES_TEXT = "; ".join(f"{s.key} = {s.label}" for s in SPACES.values())
_CATEGORIES_TEXT = "; ".join(f"{k} = {v}" for k, v in CATEGORY_LABELS.items())

SYSTEM_PROMPT = (
    "Tu es l'assistant de réservation du Collège Catholique Bilingue de la Retraite. "
    "Tu aides un client à réserver un espace du Collège (le Gymnase, la Salle des fêtes, etc.). "
    f"Espaces disponibles (clé = nom) : {_SPACES_TEXT}. "
    "Le prix dépend de l'espace, de la catégorie du client "
    f"({_CATEGORIES_TEXT}), de la durée (moins de 5 heures, ou journée au-delà) et des prestations en plus "
    "(chaises, tables, sonorisation). Une caution remboursable est versée en même temps que la location. "
    "Ne devine jamais un prix : appelle get_quote. Si le client n'a pas dit sa catégorie, demande-la. "
    "Avant toute réservation, vérifie la disponibilité avec check_availability, puis annonce le prix. "
    "N'appelle create_reservation qu'après avoir obtenu une confirmation explicite de "
    "l'utilisateur qu'il a lu et accepte le règlement intérieur du Collège (accepted_rules=true). "
    "Si le créneau est indisponible, propose la date suggérée par l'outil. "
    "Une fois la réservation créée, communique clairement son statut (en attente de validation "
    "par l'administration, sauf réservation interne), le montant à verser (location + caution) et le code de sécurité. "
    "Réponds toujours en français, de façon concise et chaleureuse."
)

_ROOM_PROP = {"type": "string", "enum": list(SPACES)}
_CATEGORY_PROP = {"type": "string", "enum": list(CATEGORY_LABELS), "description": "Catégorie tarifaire du client"}
_EXTRAS_PROP = {
    "type": "array",
    "description": "Prestations en plus (facultatif)",
    "items": {
        "type": "object",
        "properties": {"key": {"type": "string", "enum": list(EXTRAS)}, "quantity": {"type": "integer", "minimum": 1}},
        "required": ["key", "quantity"],
    },
}

TOOLS = [
    {
        "name": "check_availability",
        "description": "Vérifie si un créneau est disponible pour un espace donné avant de proposer une réservation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "room": _ROOM_PROP,
                "event_date": {"type": "string", "description": "Date au format AAAA-MM-JJ"},
                "start_time": {"type": "string", "description": "Heure de début au format HH:MM"},
                "end_time": {"type": "string", "description": "Heure de fin au format HH:MM"},
            },
            "required": ["room", "event_date", "start_time", "end_time"],
        },
    },
    {
        "name": "get_quote",
        "description": "Calcule le prix exact d'une location d'après la grille tarifaire du Collège (avec la caution).",
        "input_schema": {
            "type": "object",
            "properties": {
                "room": _ROOM_PROP,
                "start_time": {"type": "string", "description": "Heure de début au format HH:MM"},
                "end_time": {"type": "string", "description": "Heure de fin au format HH:MM"},
                "client_category": _CATEGORY_PROP,
                "extras": _EXTRAS_PROP,
            },
            "required": ["room", "start_time", "end_time", "client_category"],
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
                "room": _ROOM_PROP,
                "event_date": {"type": "string", "description": "Date au format AAAA-MM-JJ"},
                "start_time": {"type": "string", "description": "Heure de début au format HH:MM"},
                "end_time": {"type": "string", "description": "Heure de fin au format HH:MM"},
                "accepted_rules": {"type": "boolean"},
                "client_category": _CATEGORY_PROP,
                "extras": _EXTRAS_PROP,
            },
            "required": ["room", "event_date", "start_time", "end_time", "accepted_rules", "client_category"],
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


def _extras_dict(tool_input: dict) -> dict[str, int]:
    extras: dict[str, int] = {}
    for item in tool_input.get("extras") or []:
        extras[item["key"]] = extras.get(item["key"], 0) + int(item["quantity"])
    return extras


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

            if name == "get_quote":
                room = RoomType(tool_input["room"])
                quote = quote_for(
                    room,
                    tool_input.get("client_category", DEFAULT_CATEGORY),
                    parse_time(tool_input["start_time"]),
                    parse_time(tool_input["end_time"]),
                    _extras_dict(tool_input),
                )
                return tool_ok({
                    "space": room_label(room.value),
                    "client_category": category_label(quote.category),
                    "duration": "moins de 5 heures" if quote.duration_type == "short" else "journée",
                    "rental_fcfa": quote.rental,
                    "extras": [vars(line) for line in quote.extras],
                    "total_fcfa": quote.total,
                    "deposit_fcfa": quote.deposit,
                    "total_to_pay_fcfa": quote.total_due,
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
                    reservation = create_reservation(
                        db,
                        user,
                        room,
                        event_date,
                        start_time,
                        end_time,
                        client_category=tool_input.get("client_category", DEFAULT_CATEGORY),
                        extras=_extras_dict(tool_input),
                    )
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
                    "deposit": float(reservation.deposit or 0),
                    "total_to_pay": float(reservation.amount + (reservation.deposit or 0)),
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
        except (KeyError, ValueError, TariffError) as e:
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
