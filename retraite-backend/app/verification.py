"""Signature des reçus : le QR code d'un reçu pointe vers une page publique de vérification.

Le lien contient un jeton calculé avec la SECRET_KEY du serveur (HMAC) : sans cette clé, personne ne peut
fabriquer un lien valide pour un faux reçu.
"""
import hashlib
import hmac

from .config import settings


def make_token(reservation_id: int, security_code: str) -> str:
    message = f"{reservation_id}:{security_code}".encode()
    return hmac.new(settings.SECRET_KEY.encode(), message, hashlib.sha256).hexdigest()[:24]


def is_valid_token(reservation_id: int, security_code: str, token: str) -> bool:
    return hmac.compare_digest(make_token(reservation_id, security_code), token)


def verification_url(reservation_id: int, security_code: str) -> str:
    base = settings.PUBLIC_BASE_URL.rstrip("/")
    return f"{base}/verify/{reservation_id}/{make_token(reservation_id, security_code)}"
