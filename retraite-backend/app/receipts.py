import json
import os

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from .config import settings
from .models import Reservation, User
from .tariffs import DURATION_LABELS, category_label, room_label
from .verification import verification_url


def fcfa(value) -> str:
    return f"{int(value):,} FCFA".replace(",", " ")


def qr_drawing(data: str, size: float) -> Drawing:
    widget = QrCodeWidget(data, barLevel="M")
    x0, y0, x1, y1 = widget.getBounds()
    drawing = Drawing(size, size, transform=[size / (x1 - x0), 0, 0, size / (y1 - y0), 0, 0])
    drawing.add(widget)
    return drawing


def draw_qr(c: canvas.Canvas, data: str, x: float, y: float, size: float) -> None:
    renderPDF.draw(qr_drawing(data, size), c, x, y)


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

    deposit = int(reservation.deposit or 0)
    lines = [
        f"Réservation N° : {reservation.id}",
        f"Client : {user.full_name} ({user.email})",
        f"Espace : {room_label(reservation.room.value)}",
        f"Date : {reservation.event_date.isoformat()}",
        f"Horaire : {reservation.start_time.strftime('%H:%M')} - {reservation.end_time.strftime('%H:%M')}",
    ]
    if reservation.is_internal:
        lines.append("Réservation interne du Collège : aucun paiement requis.")
    else:
        extras = json.loads(reservation.extras_json) if reservation.extras_json else []
        extras_total = sum(int(e["total"]) for e in extras)
        rental = int(reservation.amount) - extras_total
        lines.append(f"Catégorie tarifaire : {category_label(reservation.client_category)}")
        lines.append(f"Durée : {DURATION_LABELS.get(reservation.duration_type, '-')}")
        lines.append(f"Location : {fcfa(rental)}")
        for e in extras:
            lines.append(f"  {e['label']} x {e['quantity']} : {fcfa(e['total'])}")
        lines.append(f"Total location : {fcfa(reservation.amount)}")
        lines.append(f"Caution remboursable : {fcfa(deposit)}")
        lines.append(f"Total à verser (location + caution) : {fcfa(int(reservation.amount) + deposit)}")
    lines += [f"Statut : {reservation.status.value}", f"Code de sécurité : {security_code}"]
    for line in lines:
        c.drawString(50, y, line)
        y -= 20

    qr_size = 120
    qr_y = y - qr_size - 30
    draw_qr(c, verification_url(reservation.id, security_code), 50, qr_y, qr_size)
    c.setFont("Helvetica", 9)
    c.drawString(50, qr_y - 14, "Scannez pour vérifier l'authenticité de ce reçu.")
    if settings.APP_DOWNLOAD_URL:
        draw_qr(c, settings.APP_DOWNLOAD_URL, 330, qr_y, qr_size)
        c.drawString(330, qr_y - 14, "Scannez pour télécharger l'application.")

    c.showPage()
    c.save()
    return path
