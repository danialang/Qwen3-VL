"""Paiement : le client choisit un moyen, seul l'administrateur (ou l'opérateur) confirme le paiement."""
import os
import sys
import tempfile
from datetime import date, timedelta

_DIR = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{_DIR}/pay.db"
os.environ["SECRET_KEY"] = "test-secret"
os.environ["ADMIN_EMAIL"] = "ecoretraite@gmail.com"
os.environ["ADMIN_PASSWORD"] = "AdminPass123!"
os.environ["CONTACT_EMAIL"] = "contact@collegedelaretraite.test"  # même valeur que test_store_requirements (settings est partagé)
os.environ["LOG_DIR"] = f"{_DIR}/logs"
os.environ["RECEIPTS_DIR"] = f"{_DIR}/receipts"
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def _login(client, email, password):
    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": "Bearer " + r.json()["access_token"]}


def _reservation(client, email, days):
    r = client.post("/auth/register", json={"email": email, "password": "ClientPass1!", "full_name": "Client Paiement"})
    assert r.status_code == 201, r.text
    headers = _login(client, email, "ClientPass1!")
    day = date.today() + timedelta(days=days)
    r = client.post("/reservations", json={"room": "tatami", "event_date": day.isoformat(), "start_time": "08:00:00",
                                          "end_time": "10:00:00", "accepted_rules": True}, headers=headers)
    assert r.status_code == 201, r.text
    return headers, r.json()["id"]


def test_options_offer_only_offline_methods_without_api_keys(client, monkeypatch):
    monkeypatch.setattr(settings, "BANK_TRANSFER_DETAILS", "")
    keys = [m["key"] for m in client.get("/payments/options").json()["methods"]]
    assert keys == ["economat"]
    monkeypatch.setattr(settings, "BANK_TRANSFER_DETAILS", "Access Bank - compte 0001")
    keys = [m["key"] for m in client.get("/payments/options").json()["methods"]]
    assert keys == ["economat", "virement"]


def test_client_cannot_mark_reservation_paid(client):
    headers, rid = _reservation(client, "paiement.economat@gmail.com", 30)
    r = client.post(f"/reservations/{rid}/pay", json={"method": "economat"}, headers=headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["reservation"]["payment_method"] == "economat"
    assert body["reservation"]["paid_at"] is None
    assert "économat" in body["message"]
    for method in ("orange_money", "mtn_momo", "access_bank", "paypal_sandbox"):
        assert client.post(f"/reservations/{rid}/pay", json={"method": method}, headers=headers).status_code == 400


def test_admin_validation_confirms_payment(client):
    headers, rid = _reservation(client, "paiement.admin@gmail.com", 31)
    client.post(f"/reservations/{rid}/pay", json={"method": "economat"}, headers=headers)
    admin = _login(client, "ecoretraite@gmail.com", "AdminPass123!")
    r = client.post(f"/reservations/{rid}/validate", json={"reference": "CAISSE-042"}, headers=admin)
    assert r.status_code == 200, r.text
    assert r.json()["paid_at"] is not None
    assert r.json()["payment_reference"] == "CAISSE-042"
    assert client.post(f"/reservations/{rid}/pay", json={"method": "economat"}, headers=headers).status_code == 400


def test_webhook_rejects_unconfigured_provider(client):
    assert client.post("/payments/webhook/orange_money", content=b"{}").status_code == 404
