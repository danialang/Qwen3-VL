"""Exigences des boutiques d'applications : pages légales et suppression de compte."""
import os
import sys
import tempfile
from datetime import date, timedelta

_DIR = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{_DIR}/store.db"
os.environ["SECRET_KEY"] = "test-secret"
os.environ["ADMIN_EMAIL"] = "ecoretraite@gmail.com"
os.environ["ADMIN_PASSWORD"] = "AdminPass123!"
os.environ["CONTACT_EMAIL"] = "contact@collegedelaretraite.test"
os.environ["LOG_DIR"] = f"{_DIR}/logs"
os.environ["RECEIPTS_DIR"] = f"{_DIR}/receipts"
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def _login(client, email, password):
    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": "Bearer " + r.json()["access_token"]}


def _register(client, email, name="Client Boutique"):
    r = client.post("/auth/register", json={"email": email, "password": "ClientPass1!", "full_name": name, "phone": "690000000"})
    assert r.status_code == 201, r.text
    return _login(client, email, "ClientPass1!")


def test_legal_pages_are_public_and_complete(client):
    privacy = client.get("/privacy")
    assert privacy.status_code == 200 and "text/html" in privacy.headers["content-type"]
    assert "Politique de confidentialité" in privacy.text
    assert "contact@collegedelaretraite.test" in privacy.text
    for word in ("Anthropic", "supprimer", "HTTPS"):
        assert word.lower() in privacy.text.lower()
    deletion = client.get("/account-deletion")
    assert deletion.status_code == 200
    assert "Supprimer mon compte" in deletion.text


def test_delete_account_erases_personal_data_but_keeps_anonymous_reservations(client):
    admin = _login(client, "ecoretraite@gmail.com", "AdminPass123!")
    headers = _register(client, "suppression.compte@gmail.com", "Marie Suppression")
    day = date.today() + timedelta(days=20)
    r = client.post("/reservations", json={"room": "tatami", "event_date": day.isoformat(), "start_time": "08:00:00",
                                          "end_time": "10:00:00", "accepted_rules": True}, headers=headers)
    assert r.status_code == 201
    reservation_id = r.json()["id"]

    # mauvais mot de passe : refusé
    assert client.post("/auth/delete-account", json={"password": "Mauvais1!"}, headers=headers).status_code == 400

    # réservation en attente : le compte peut être supprimé, la réservation est annulée
    ok = client.post("/auth/delete-account", json={"password": "ClientPass1!"}, headers=headers)
    assert ok.status_code == 200, ok.text

    # plus de connexion possible
    assert client.post("/auth/login", json={"email": "suppression.compte@gmail.com", "password": "ClientPass1!"}).status_code in (400, 401)
    users = client.get("/auth/users", headers=admin).json()
    assert not any("suppression.compte" in u["email"] or "Marie" in u["full_name"] for u in users)
    assert any(u["full_name"] == "Compte supprimé" and u["phone"] is None for u in users)
    res = client.get(f"/reservations/{reservation_id}", headers=admin).json()
    assert res["status"] == "cancelled"

    # l'email peut être réutilisé pour un nouveau compte
    _register(client, "suppression.compte@gmail.com")


def test_delete_account_is_refused_with_a_validated_upcoming_reservation(client):
    admin = _login(client, "ecoretraite@gmail.com", "AdminPass123!")
    headers = _register(client, "reservation.validee@gmail.com")
    day = date.today() + timedelta(days=25)
    rid = client.post("/reservations", json={"room": "tatami", "event_date": day.isoformat(), "start_time": "08:00:00",
                                            "end_time": "10:00:00", "accepted_rules": True}, headers=headers).json()["id"]
    assert client.post(f"/reservations/{rid}/validate", headers=admin).status_code == 200
    refused = client.post("/auth/delete-account", json={"password": "ClientPass1!"}, headers=headers)
    assert refused.status_code == 400 and "réservation validée" in refused.json()["detail"]
    # une fois annulée, la suppression passe
    assert client.post(f"/reservations/{rid}/cancel", headers=headers).status_code == 200
    assert client.post("/auth/delete-account", json={"password": "ClientPass1!"}, headers=headers).status_code == 200


def test_admin_accounts_cannot_be_deleted_from_the_app(client):
    admin = _login(client, "ecoretraite@gmail.com", "AdminPass123!")
    assert client.post("/auth/delete-account", json={"password": "AdminPass123!"}, headers=admin).status_code == 403
