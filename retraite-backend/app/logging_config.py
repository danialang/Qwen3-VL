import logging
import os

from .config import settings

LOG_FILE = os.path.join(settings.LOG_DIR, "app.log")

_configured = False


def setup_logging() -> None:
    global _configured
    if _configured:
        return
    handlers = [logging.StreamHandler()]
    try:
        os.makedirs(settings.LOG_DIR, exist_ok=True)
        handlers.append(logging.FileHandler(LOG_FILE, encoding="utf-8"))
    except OSError:
        pass  # disque en lecture seule chez l'hébergeur : les logs restent dans la console
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=handlers,
    )
    _configured = True


def read_recent_logs(lines: int = 50) -> str:
    if not os.path.exists(LOG_FILE):
        return "Aucun log disponible pour le moment."
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        all_lines = f.readlines()
    if not all_lines:
        return "Aucun log disponible pour le moment."
    return "".join(all_lines[-lines:])
