import re

from fastapi import HTTPException, status

# Fournisseurs d'email acceptés à l'inscription (garder cette liste identique à celle de l'appli mobile).
ALLOWED_EMAIL_DOMAINS = {
    "gmail.com", "googlemail.com",
    "icloud.com", "me.com", "mac.com",
    "outlook.com", "outlook.fr", "hotmail.com", "hotmail.fr", "live.com", "live.fr",
    "yahoo.com", "yahoo.fr",
    "proton.me", "protonmail.com",
}

# Lettres uniquement (accents compris), séparées par des espaces, tirets ou apostrophes.
_NAME_RE = re.compile(r"^[^\W\d_]+(?:[ '’\-][^\W\d_]+)*$")


def validate_full_name(name: str) -> None:
    name = name.strip()
    if len(name) < 2 or not _NAME_RE.fullmatch(name):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Le nom ne doit contenir que des lettres (pas de chiffres ni de symboles).",
        )


def validate_email_provider(email: str) -> None:
    domain = email.rsplit("@", 1)[-1].lower()
    if domain not in ALLOWED_EMAIL_DOMAINS:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Adresse email non valide : utilisez une vraie adresse, par exemple nom@gmail.com ou nom@icloud.com.",
        )
