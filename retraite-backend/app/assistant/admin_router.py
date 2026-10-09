from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..logging_config import read_recent_logs
from ..models import User, UserRole
from ..security import require_roles
from ..stats import annual_report, pending_reservations, reservations_this_month
from .common import get_anthropic_client, run_tool_loop, tool_error, tool_ok

router = APIRouter(prefix="/assistant/admin", tags=["assistant"])

SYSTEM_PROMPT = (
    "Tu es l'assistant d'administration du Collège Catholique Bilingue de la Retraite, réservé "
    "à l'équipe admin. Tu réponds à des questions en langage naturel sur les réservations "
    "(comptages, réservations en attente), tu génères le bilan de fin d'année sur demande "
    "(taux d'occupation par salle, revenus, nombre de réservations par type), et tu aides au "
    "diagnostic de bugs en lisant les logs applicatifs récents. "
    "Donne des chiffres exacts issus des outils, jamais estimés. Réponds en français, de façon "
    "claire et structurée (utilise des listes si utile)."
)

TOOLS = [
    {
        "name": "count_reservations_this_month",
        "description": "Retourne le nombre de réservations (toutes salles, tous statuts) créées pour le mois en cours.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "list_pending_reservations",
        "description": "Liste les réservations externes en attente de validation par l'administration.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_annual_report",
        "description": (
            "Génère le bilan annuel : nombre de réservations par salle et par statut, revenus "
            "totaux, réservations internes/externes, taux d'occupation par salle."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"year": {"type": "integer", "description": "Année (ex. 2026)"}},
            "required": ["year"],
        },
    },
    {
        "name": "read_app_logs",
        "description": "Lit les dernières lignes des logs applicatifs, utile pour diagnostiquer un bug ou une erreur récente.",
        "input_schema": {
            "type": "object",
            "properties": {
                "lines": {"type": "integer", "description": "Nombre de lignes à lire (défaut 50, max 300)"}
            },
        },
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


def _make_executor(db: Session):
    def executor(name: str, tool_input: dict) -> tuple[str, bool]:
        try:
            if name == "count_reservations_this_month":
                return tool_ok({"count": reservations_this_month(db)})

            if name == "list_pending_reservations":
                items = pending_reservations(db)
                return tool_ok({
                    "pending_reservations": [
                        {
                            "id": r.id,
                            "room": r.room.value,
                            "event_date": r.event_date.isoformat(),
                            "user_id": r.user_id,
                            "amount": float(r.amount),
                        }
                        for r in items
                    ]
                })

            if name == "get_annual_report":
                year = int(tool_input["year"])
                return tool_ok(annual_report(db, year))

            if name == "read_app_logs":
                lines = min(int(tool_input.get("lines") or 50), 300)
                return tool_ok({"logs": read_recent_logs(lines)})

            return tool_error(f"Outil inconnu : {name}")
        except (KeyError, ValueError) as e:
            return tool_error(f"Paramètres invalides : {e}")

    return executor


@router.post("", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.dev)),
):
    client = get_anthropic_client()
    messages = [{"role": m.role, "content": m.content} for m in payload.history]
    messages.append({"role": "user", "content": payload.message})

    reply = run_tool_loop(client, SYSTEM_PROMPT, TOOLS, messages, _make_executor(db))

    new_history = payload.history + [
        ChatMessage(role="user", content=payload.message),
        ChatMessage(role="assistant", content=reply),
    ]
    return ChatResponse(reply=reply, history=new_history)
