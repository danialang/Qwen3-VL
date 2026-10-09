from .config import settings
from .database import SessionLocal
from .models import User, UserRole
from .security import hash_password, validate_password_strength


def _ensure_user(db, email, password, full_name, role):
    if not email or not password:
        return
    if db.query(User).filter(User.email == email).first():
        return
    validate_password_strength(password)
    db.add(User(email=email, password_hash=hash_password(password), full_name=full_name, role=role))
    db.commit()


def seed_initial_users():
    db = SessionLocal()
    try:
        _ensure_user(db, settings.DEV_EMAIL, settings.DEV_PASSWORD, "Développeur", UserRole.dev)
        _ensure_user(db, settings.ADMIN_EMAIL, settings.ADMIN_PASSWORD, "Admin Collège", UserRole.admin)
    finally:
        db.close()


if __name__ == "__main__":
    seed_initial_users()
