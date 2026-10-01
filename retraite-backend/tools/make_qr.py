"""Fabrique un QR code imprimable (PDF + SVG) à partir d'un lien.

Exemple (QR de l'appli, quand elle sera sur le Play Store) :
    python tools/make_qr.py "https://play.google.com/store/apps/details?id=..." app_playstore
Crée app_playstore.pdf et app_playstore.svg.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from reportlab.graphics import renderPDF, renderSVG  # noqa: E402

from app.receipts import qr_drawing  # noqa: E402


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit('Utilisation : python tools/make_qr.py "<lien>" <nom_du_fichier_sans_extension>')
    url, name = sys.argv[1], sys.argv[2]
    drawing = qr_drawing(url, 300)
    renderPDF.drawToFile(drawing, f"{name}.pdf")
    renderSVG.drawToFile(drawing, f"{name}.svg")
    print(f"QR code créé : {name}.pdf et {name}.svg")


if __name__ == "__main__":
    main()
