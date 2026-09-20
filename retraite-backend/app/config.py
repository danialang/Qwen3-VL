import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:@127.0.0.1:3306/retraite_db")
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
    RESERVATION_AMOUNT = int(os.getenv("RESERVATION_AMOUNT", "5000000"))
    RECEIPTS_DIR = os.getenv("RECEIPTS_DIR", "receipts")

    DEV_EMAIL = os.getenv("DEV_EMAIL")
    DEV_PASSWORD = os.getenv("DEV_PASSWORD")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "ecoretraite@gmail.com")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")


settings = Settings()
