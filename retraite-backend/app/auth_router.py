import hashlib
import hmac
import logging
import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .emailer import send_email, smtp_configured
from .models import PasswordReset, User, UserRole
from .schemas import (
    ForgotPasswordRequest,
    LoginRequest,
    PasswordChange,
    ResetPasswordRequest,
    Token,
    UserCreate,
    UserOut,
)
from .security import (
    create_access_token,
    get_current_user,
    hash_password,
    require_roles,
    validate_password_strength,
    verify_password,
)
from .validators import validate_email_provider, validate_full_name

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger("retraite.auth")


def _find_user(db: Session, email: str) -> User | None:
    """Recherche par email sans tenir compte des majuscules (les claviers en ajoutent souvent)."""
    return db.query(User).filter(func.lower(User.email) == email.strip().lower()).first()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    validate_full_name(payload.full_name)
    validate_email_provider(payload.email)
    if _find_user(db, payload.email):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Un compte existe déjà avec cet email.")

    validate_password_strength(payload.password)

    user = User(
        email=payload.email.strip().lower(),
        password_hash=hash_password(payload.password),
        full_name=payload.full_name.strip(),
        phone=payload.phone,
        role=UserRole.client,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("Nouveau compte client inscrit : user_id=%s email=%s", user.id, user.email)
    return user


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = _find_user(db, payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        logger.warning("Échec de connexion pour email=%s", payload.email)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Email ou mot de passe incorrect.")

    logger.info("Connexion réussie : user_id=%s role=%s", user.id, user.role.value)
    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return Token(access_token=token)


RESET_CODE_VALIDITY_MINUTES = 15
RESET_MAX_ATTEMPTS = 5
RESET_RESEND_DELAY_SECONDS = 60
FORGOT_PASSWORD_ANSWER = {"detail": "Si un compte existe avec cet email, un code de vérification vient d'être envoyé."}


def _hash_reset_code(user_id: int, code: str) -> str:
    return hmac.new(settings.SECRET_KEY.encode(), f"{user_id}:{code}".encode(), hashlib.sha256).hexdigest()


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    # Même réponse que le compte existe ou non : on ne révèle jamais quels emails sont inscrits.
    user = _find_user(db, payload.email)
    if not user:
        logger.warning("Mot de passe oublié demandé pour un email inconnu : %s", payload.email)
        return FORGOT_PASSWORD_ANSWER

    last = db.query(PasswordReset).filter(PasswordReset.user_id == user.id).order_by(PasswordReset.id.desc()).first()
    if last and (datetime.utcnow() - last.created_at).total_seconds() < RESET_RESEND_DELAY_SECONDS:
        return FORGOT_PASSWORD_ANSWER

    db.query(PasswordReset).filter(PasswordReset.user_id == user.id, PasswordReset.used.is_(False)).update({"used": True})
    code = f"{secrets.randbelow(10**6):06d}"
    db.add(
        PasswordReset(
            user_id=user.id,
            code_hash=_hash_reset_code(user.id, code),
            expires_at=datetime.utcnow() + timedelta(minutes=RESET_CODE_VALIDITY_MINUTES),
        )
    )
    db.commit()

    sent = send_email(
        user.email,
        "Collège de la Retraite : code de réinitialisation du mot de passe",
        f"Bonjour {user.full_name},\n\n"
        f"Votre code de vérification est : {code}\n"
        f"Il est valable {RESET_CODE_VALIDITY_MINUTES} minutes.\n\n"
        "Si vous n'avez pas demandé ce code, ignorez ce message : votre mot de passe reste inchangé.\n\n"
        "Collège Catholique Bilingue de la Retraite",
    )
    if not sent and settings.RESET_CODE_IN_LOGS and not smtp_configured():
        logger.warning("[DEV] Code de réinitialisation pour %s : %s", user.email, code)
    logger.info("Code de réinitialisation créé : user_id=%s email_envoye=%s", user.id, sent)
    return FORGOT_PASSWORD_ANSWER


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    invalid = HTTPException(status.HTTP_400_BAD_REQUEST, "Code invalide ou expiré.")
    user = _find_user(db, payload.email)
    if not user:
        raise invalid

    reset = (
        db.query(PasswordReset)
        .filter(PasswordReset.user_id == user.id, PasswordReset.used.is_(False))
        .order_by(PasswordReset.id.desc())
        .first()
    )
    if not reset or reset.expires_at < datetime.utcnow() or reset.attempts >= RESET_MAX_ATTEMPTS:
        raise invalid

    if not hmac.compare_digest(reset.code_hash, _hash_reset_code(user.id, payload.code.strip())):
        reset.attempts += 1
        db.commit()
        logger.warning("Mauvais code de réinitialisation : user_id=%s (essai %s)", user.id, reset.attempts)
        raise invalid

    validate_password_strength(payload.new_password)
    user.password_hash = hash_password(payload.new_password)
    reset.used = True
    db.commit()
    logger.info("Mot de passe réinitialisé par code : user_id=%s", user.id)
    return {"detail": "Mot de passe modifié."}


@router.post("/change-password")
def change_password(
    payload: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(payload.current_password, current_user.password_hash):
        logger.warning("Changement de mot de passe refusé (ancien mot de passe faux) : user_id=%s", current_user.id)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Le mot de passe actuel est incorrect.")
    validate_password_strength(payload.new_password)
    if payload.new_password == payload.current_password:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Le nouveau mot de passe doit être différent de l'ancien.")

    current_user.password_hash = hash_password(payload.new_password)
    db.commit()
    logger.info("Mot de passe modifié : user_id=%s", current_user.id)
    return {"detail": "Mot de passe modifié."}


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/users", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.dev)),
):
    return db.query(User).order_by(User.created_at.desc()).all()
