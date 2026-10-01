import os

from dotenv import load_dotenv

load_dotenv()


def _database_url() -> str:
    # Les hébergeurs (Railway...) fournissent "mysql://..." ; SQLAlchemy a besoin du pilote pymysql.
    url = os.getenv("DATABASE_URL") or os.getenv("MYSQL_URL") or "mysql+pymysql://root:@127.0.0.1:3306/retraite_db"
    if url.startswith("mysql://"):
        url = "mysql+pymysql://" + url[len("mysql://"):]
    return url


class Settings:
    DATABASE_URL = _database_url()
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
    RESERVATION_AMOUNT = int(os.getenv("RESERVATION_AMOUNT", "5000000"))
    RECEIPTS_DIR = os.getenv("RECEIPTS_DIR", "receipts")
    LOG_DIR = os.getenv("LOG_DIR", "logs")

    DEV_EMAIL = os.getenv("DEV_EMAIL")
    DEV_PASSWORD = os.getenv("DEV_PASSWORD")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "ecoretraite@gmail.com")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

    # Adresse publique du serveur : elle est écrite dans le QR code des reçus.
    PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000")
    # Lien de téléchargement de l'appli (Play Store) : si rempli, un 2e QR code apparaît sur le reçu.
    APP_DOWNLOAD_URL = os.getenv("APP_DOWNLOAD_URL", "")

    # Envoi d'emails (code "mot de passe oublié"). Gmail : smtp.gmail.com, port 587, mot de passe d'application.
    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM = os.getenv("SMTP_FROM", "")
    SMTP_STARTTLS = os.getenv("SMTP_STARTTLS", "true").lower() == "true"
    # DÉVELOPPEMENT UNIQUEMENT : écrit le code dans les logs du serveur quand aucun email ne peut partir.
    RESET_CODE_IN_LOGS = os.getenv("RESET_CODE_IN_LOGS", "false").lower() == "true"

    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    ASSISTANT_MODEL = os.getenv("ASSISTANT_MODEL", "claude-sonnet-5-5")


settings = Settings()
