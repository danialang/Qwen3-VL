import os

from dotenv import load_dotenv

load_dotenv()


def _database_url() -> str:
    # Les hébergeurs (Railway...) fournissent "mysql://..." ; SQLAlchemy a besoin du pilote pymysql.
    url = os.getenv("DATABASE_URL") or os.getenv("MYSQL_URL") or "mysql+pymysql://root:@127.0.0.1:3306/retraite_db"
    if url.startswith("mysql://"):
        url = "mysql+pymysql://" + url[len("mysql://"):]
    return url


DEFAULT_SECRET_KEY = "change-me"


class Settings:
    APP_ENV = os.getenv("APP_ENV", "development").lower()
    DATABASE_URL = _database_url()
    SECRET_KEY = os.getenv("SECRET_KEY", DEFAULT_SECRET_KEY)
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
    RESERVATION_AMOUNT = int(os.getenv("RESERVATION_AMOUNT", "5000000"))
    RECEIPTS_DIR = os.getenv("RECEIPTS_DIR", "receipts")
    LOG_DIR = os.getenv("LOG_DIR", "logs")

    DEV_EMAIL = os.getenv("DEV_EMAIL")
    DEV_PASSWORD = os.getenv("DEV_PASSWORD")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "ecoretraite@gmail.com")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    ASSISTANT_MODEL = os.getenv("ASSISTANT_MODEL", "claude-sonnet-5-5")


settings = Settings()

# En ligne, une clé par défaut permettrait à n'importe qui de forger un jeton admin : on refuse de démarrer.
if settings.APP_ENV == "production" and settings.SECRET_KEY in (DEFAULT_SECRET_KEY, "change-me-to-a-random-secret", ""):
    raise RuntimeError("SECRET_KEY doit être défini (valeur aléatoire) quand APP_ENV=production.")
