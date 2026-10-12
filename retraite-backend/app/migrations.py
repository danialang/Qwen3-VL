"""Mise à jour automatique de la base au démarrage.

`Base.metadata.create_all` crée les tables manquantes mais ne modifie jamais une table existante.
Quand une version de l'application ajoute des colonnes ou des valeurs, on les applique ici, sans perdre les données.
"""
import logging

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

from .models import RoomType

logger = logging.getLogger("retraite.migrations")

NEW_RESERVATION_COLUMNS = {
    "deposit": "NUMERIC(12, 2) NOT NULL DEFAULT 0",
    "client_category": "VARCHAR(30) NULL",
    "duration_type": "VARCHAR(10) NULL",
    "extras_json": "TEXT NULL",
}


def ensure_schema(engine: Engine) -> None:
    inspector = inspect(engine)
    if not inspector.has_table("reservations"):
        return

    columns = {c["name"]: c for c in inspector.get_columns("reservations")}
    statements: list[str] = []

    for name, ddl in NEW_RESERVATION_COLUMNS.items():
        if name not in columns:
            statements.append(f"ALTER TABLE reservations ADD COLUMN {name} {ddl}")

    # MySQL stocke « room » dans une colonne ENUM : on y ajoute les nouveaux espaces.
    if engine.dialect.name == "mysql":
        known = set(getattr(columns["room"]["type"], "enums", []) or [])
        wanted = [r.name for r in RoomType]
        if known != set(wanted):
            values = ", ".join("'" + v + "'" for v in wanted)
            statements.append(f"ALTER TABLE reservations MODIFY COLUMN room ENUM({values}) NOT NULL")

    if not statements:
        return
    with engine.begin() as conn:
        for statement in statements:
            logger.info("Migration : %s", statement)
            conn.execute(text(statement))
