FROM python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

# (L'image python:slim contient déjà ca-certificates, utile pour une base MySQL hébergée en TLS.)

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# L'application ne tourne pas en administrateur dans le conteneur.
RUN useradd --create-home appuser && mkdir -p /app/receipts /app/logs && chown -R appuser /app
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:%s/health' % os.environ.get('PORT','8000'), timeout=3)"

# L'hébergeur fournit le port dans $PORT (8000 par défaut en local).
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
