import os

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from .config import settings
from .models import Reservation, User

ROOM_LABELS = {"gymnase": "Gymnase", "salle_fetes": "Salle des fêtes"}


def generate_receipt_pdf(reservation: Reservation, security_code: str, user: User) -> str:
    os.makedirs(settings.RECEIPTS_DIR, exist_ok=True)
    path = os.path.join(settings.RECEIPTS_DIR, f"recu_{reservation.id}.pdf")

    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    y = height - 60

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Collège Catholique Bilingue de la Retraite")
    y -= 25
    c.setFont("Helvetica", 12)
    c.drawString(50, y, "Reçu de réservation")
    y -= 35

    amount = int(reservation.amount)
    lines = [
        f"Réservation N° : {reservation.id}",
        f"Client : {user.full_name} ({user.email})",
        f"Salle : {ROOM_LABELS[reservation.room.value]}",
        f"Date : {reservation.event_date.isoformat()}",
        f"Horaire : {reservation.start_time.strftime('%H:%M')} - {reservation.end_time.strftime('%H:%M')}",
        f"Montant : {amount:,} FCFA".replace(",", " "),
        f"Statut : {reservation.status.value}",
        f"Code de sécurité : {security_code}",
    ]
    for line in lines:
        c.drawString(50, y, line)
        y -= 20

    c.showPage()
    c.save()
    return path
