FROM python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_ENV=production

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Pas de root dans le conteneur ; l'utilisateur doit pouvoir écrire les reçus PDF et les logs.
RUN useradd --system --no-create-home appuser \
    && mkdir -p receipts logs \
    && chown -R appuser /app
USER appuser

# L'hébergeur fournit le port dans $PORT (8000 par défaut en local).
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD ["sh", "-c", "python -c \"import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.getenv('PORT', '8000') + '/health', timeout=4)\""]

# --forwarded-allow-ips : le proxy HTTPS de l'hébergeur est de confiance (bon schéma/IP client).
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips='*'"]
