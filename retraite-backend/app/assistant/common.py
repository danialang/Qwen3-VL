import json
import logging
from datetime import date as date_cls
from datetime import time as time_cls

import anthropic
from fastapi import HTTPException, status

from ..config import settings

MAX_TOOL_ITERATIONS = 6
logger = logging.getLogger("retraite.assistant")


def get_anthropic_client() -> anthropic.Anthropic:
    if not settings.ANTHROPIC_API_KEY:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Assistant IA non configuré (ANTHROPIC_API_KEY manquante côté serveur).",
        )
    return anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


def parse_date(value: str) -> date_cls:
    return date_cls.fromisoformat(value)


def parse_time(value: str) -> time_cls:
    parts = value.split(":")
    return time_cls(hour=int(parts[0]), minute=int(parts[1]))


def run_tool_loop(client: anthropic.Anthropic, system_prompt: str, tools: list[dict], messages: list[dict], executor) -> str:
    """Boucle agentique manuelle : appelle Claude, exécute les tool_use via `executor`,
    renvoie les résultats, jusqu'à une réponse finale (ou MAX_TOOL_ITERATIONS atteint)."""
    response = None
    for _ in range(MAX_TOOL_ITERATIONS):
        try:
            response = client.messages.create(
                model=settings.ASSISTANT_MODEL,
                max_tokens=1024,
                system=system_prompt,
                tools=tools,
                messages=messages,
            )
        except anthropic.AuthenticationError:
            logger.error("Clé API Anthropic invalide.")
            raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Assistant IA indisponible (clé API invalide).")
        except anthropic.RateLimitError:
            logger.warning("Limite de débit atteinte sur l'API Anthropic.")
            raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Assistant IA temporairement surchargé, réessayez dans un instant.")
        except (anthropic.APIConnectionError, anthropic.APIStatusError) as e:
            logger.error("Erreur API Anthropic : %s", e)
            raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Assistant IA temporairement indisponible.")

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            break

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result_text, is_error = executor(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result_text,
                    "is_error": is_error,
                })
        messages.append({"role": "user", "content": tool_results})
    else:
        return "Désolé, votre demande est trop complexe pour être traitée en une seule fois. Pouvez-vous la reformuler plus simplement ?"

    if response is None:
        return "Désolé, je n'ai pas pu traiter votre demande."

    reply = next((b.text for b in response.content if b.type == "text"), "")
    return reply or "D'accord."


def tool_error(message: str) -> tuple[str, bool]:
    return json.dumps({"error": message}, ensure_ascii=False), True


def tool_ok(payload: dict) -> tuple[str, bool]:
    return json.dumps(payload, ensure_ascii=False), False
