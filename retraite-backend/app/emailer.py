import logging
import smtplib
from email.message import EmailMessage

from .config import settings

logger = logging.getLogger("retraite.email")


def smtp_configured() -> bool:
    return bool(settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASSWORD)


def send_email(to: str, subject: str, body: str) -> bool:
    """Envoie un email texte. Renvoie False (sans lever d'erreur) si l'envoi échoue ou n'est pas configuré."""
    if not smtp_configured():
        logger.warning("SMTP non configuré : email '%s' non envoyé.", subject)
        return False

    message = EmailMessage()
    message["From"] = settings.SMTP_FROM or settings.SMTP_USER
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    try:
        if settings.SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15)
        else:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15)
            if settings.SMTP_STARTTLS:
                server.starttls()
        with server:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(message)
    except Exception:
        logger.exception("Échec d'envoi de l'email '%s'", subject)
        return False

    logger.info("Email '%s' envoyé.", subject)
    return True
