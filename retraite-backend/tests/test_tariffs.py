"""Tests de la grille tarifaire : calcul des prix, API, migration de la base.

Lancer : cd retraite-backend && pip install pytest httpx && python -m pytest tests
"""
import os
import sys
import tempfile
from datetime import date, time, timedelta

_DIR = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{_DIR}/test.db"
os.environ["SECRET_KEY"] = "test-secret"
os.environ["ADMIN_EMAIL"] = "ecoretraite@gmail.com"
os.environ["ADMIN_PASSWORD"] = "AdminPass123!"
os.environ["LOG_DIR"] = f"{_DIR}/logs"
os.environ["RECEIPTS_DIR"] = f"{_DIR}/receipts"
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect, text

from app import tariffs
from app.main import app
from app.migrations import ensure_schema
from app.models import RoomType


def test_every_room_has_a_tariff_and_the_other_way_round():
    assert {r.value for r in RoomType} == set(tariffs.SPACES)


def test_duration_threshold_is_five_hours():
    assert tariffs.duration_type(time(9), time(14)) == "short"
    assert tariffs.duration_type(time(9), time(14, 1)) == "day"
    with pytest.raises(tariffs.TariffError):
        tariffs.duration_type(time(10), time(10))


@pytest.mark.parametrize(
    "room,category,start,end,expected",
    [
        ("gymnase", "personnel_college", time(8), time(18), 1_000_000),
        ("gymnase", "personnel_exterieur", time(8), time(18), 1_500_000),
        ("gymnase", "partenaire_public", time(8), time(18), 2_000_000),
        ("gymnase", "partenaire_prive", time(8), time(12), 1_000_000),
        ("salle_fetes", "personnel_exterieur", time(8), time(22), 5_000_000),
        ("salle_fetes", "personnel_exterieur", time(8), time(12), 2_500_000),
        ("salle_reunion", "partenaire_public", time(8), time(18), 4_000_000),
        ("cours_college", "partenaire_prive", time(8), time(18), 500_000),
        ("tatami", "partenaire_prive", time(8), time(18), 50_000),
    ],
)
def test_prices_follow_the_grid(room, category, start, end, expected):
    assert tariffs.compute_quote(room, category, start, end).rental == expected


def test_extras_and_deposit():
    q = tariffs.compute_quote(
        "gymnase", "personnel_exterieur", time(8), time(12),
        {"chaise_vip_napoleon": 100, "sonorisation_complete": 1},
    )
    assert q.rental == 750_000
    assert q.extras_total == 100 * 2_000 + 350_000
    assert q.total == 750_000 + 550_000
    assert q.deposit == 500_000
    assert q.total_due == q.total + 500_000


def test_invalid_requests_are_refused():
    with pytest.raises(tariffs.TariffError):
        tariffs.compute_quote("gymnase", "inconnue", time(8), time(12))
    with pytest.raises(tariffs.TariffError):
        tariffs.compute_quote("gymnase", "partenaire_public", time(8), time(12), {"licorne": 1})
    with pytest.raises(tariffs.TariffError):
        tariffs.compute_quote("tatami", "partenaire_public", time(8), time(12), {"table_simple": 1})
    with pytest.raises(tariffs.TariffError):
        tariffs.compute_quote("gymnase", "partenaire_public", time(8), time(12), {"table_simple": 0})


def test_gymnase_and_external_classes_share_the_same_place():
    assert set(tariffs.venue_rooms("gymnase")) == {"gymnase", "cours_externe_gymnase"}
    assert "salle_reunion" in tariffs.venue_rooms("salle_fetes")
    assert tariffs.venue_rooms("tatami") == ["tatami"]


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def _login(client, email, password):
    return {"Authorization": "Bearer " + client.post("/auth/login", json={"email": email, "password": password}).json()["access_token"]}


@pytest.fixture(scope="module")
def admin(client):
    return _login(client, "ecoretraite@gmail.com", "AdminPass123!")


@pytest.fixture(scope="module")
def customer(client):
    r = client.post("/auth/register", json={"email": "client.tarifs@gmail.com", "password": "ClientPass1!", "full_name": "Client Tarifs"})
    assert r.status_code == 201, r.text
    return _login(client, "client.tarifs@gmail.com", "ClientPass1!")


def _body(room="gymnase", day=None, start="08:00:00", end="12:00:00", **extra):
    return {
        "room": room,
        "event_date": (day or date.today() + timedelta(days=30)).isoformat(),
        "start_time": start,
        "end_time": end,
        "accepted_rules": True,
        **extra,
    }


def test_catalog_is_public(client):
    data = client.get("/tariffs").json()
    assert data["deposit"] == 500_000
    assert len(data["categories"]) == 4
    assert {s["key"] for s in data["spaces"]} == set(tariffs.SPACES)
    assert "appartement" not in str(data).lower() and "chambre" not in str(data).lower() and "cuisine" not in str(data).lower()


def test_quote_endpoint(client, customer):
    r = client.post(
        "/reservations/quote",
        json={"room": "gymnase", "start_time": "08:00:00", "end_time": "12:00:00", "client_category": "partenaire_public",
              "extras": [{"key": "table_simple", "quantity": 10}]},
        headers=customer,
    )
    assert r.status_code == 200, r.text
    q = r.json()
    assert (q["rental"], q["extras_total"], q["total"], q["deposit"], q["total_due"]) == (1_000_000, 20_000, 1_020_000, 500_000, 1_520_000)
    assert q["duration_label"] == "Moins de 5 heures"
    bad = client.post("/reservations/quote", json={"room": "gymnase", "start_time": "08:00:00", "end_time": "12:00:00", "client_category": "xx"}, headers=customer)
    assert bad.status_code == 400


def test_client_reservation_is_priced_and_receipt_has_the_breakdown(client, customer, admin):
    r = client.post(
        "/reservations",
        json=_body("salle_fetes", date.today() + timedelta(days=40), "08:00:00", "23:00:00",
                   client_category="personnel_exterieur", extras=[{"key": "chaise_vip_prestige", "quantity": 20}]),
        headers=customer,
    )
    assert r.status_code == 201, r.text
    res = r.json()
    assert float(res["amount"]) == 5_000_000 + 20 * 5_000
    assert float(res["deposit"]) == 500_000
    assert float(res["total_due"]) == 5_600_000
    assert res["duration_type"] == "day" and res["status"] == "pending"
    assert res["client_category_label"] == "Personnel extérieur"
    assert res["extras"][0]["quantity"] == 20

    v = client.post(f"/reservations/{res['id']}/validate", headers=admin)
    assert v.status_code == 200
    pdf = client.get(f"/reservations/{res['id']}/receipt", headers=customer)
    assert pdf.status_code == 200 and pdf.content[:4] == b"%PDF"


def test_invalid_category_or_extra_is_refused(client, customer):
    day = date.today() + timedelta(days=50)
    assert client.post("/reservations", json=_body(day=day, client_category="roi"), headers=customer).status_code == 400
    assert client.post("/reservations", json=_body("tatami", day, extras=[{"key": "table_simple", "quantity": 1}]), headers=customer).status_code == 400


def test_internal_reservation_is_free(client, admin):
    r = client.post("/reservations", json=_body(day=date.today() + timedelta(days=60)), headers=admin)
    assert r.status_code == 201, r.text
    res = r.json()
    assert float(res["amount"]) == 0 and float(res["deposit"]) == 0 and res["is_internal"]


def test_external_classes_conflict_with_the_gymnase(client, customer):
    day = date.today() + timedelta(days=70)
    assert client.post("/reservations", json=_body("gymnase", day), headers=customer).status_code == 201
    clash = client.post("/reservations", json=_body("cours_externe_gymnase", day, "09:00:00", "11:00:00"), headers=customer)
    assert clash.status_code == 409
    other = client.post("/reservations", json=_body("tatami", day, "09:00:00", "11:00:00"), headers=customer)
    assert other.status_code == 201


def test_availability_includes_the_whole_place(client, customer):
    day = date.today() + timedelta(days=70)
    slots = client.get("/reservations/availability", params={"room": "cours_externe_gymnase"}, headers=customer).json()
    assert any(s["event_date"] == day.isoformat() and s["room"] == "gymnase" for s in slots)


def test_migration_upgrades_an_old_database():
    engine = create_engine(f"sqlite:///{_DIR}/old.db")
    with engine.begin() as conn:
        conn.execute(text(
            "CREATE TABLE reservations (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, room VARCHAR(11) NOT NULL, "
            "event_date DATE NOT NULL, start_time TIME NOT NULL, end_time TIME NOT NULL, status VARCHAR(9) NOT NULL, "
            "amount NUMERIC(12,2) NOT NULL, is_internal BOOLEAN NOT NULL, accepted_rules BOOLEAN NOT NULL, "
            "payment_method VARCHAR(50), payment_reference VARCHAR(255), paid_at DATETIME, created_at DATETIME)"
        ))
        conn.execute(text(
            "INSERT INTO reservations VALUES (1, 1, 'gymnase', '2026-01-01', '08:00', '10:00', 'validated', 5000000, 0, 1, NULL, NULL, NULL, NULL)"
        ))
    ensure_schema(engine)
    ensure_schema(engine)  # sans danger si on le relance
    cols = {c["name"] for c in inspect(engine).get_columns("reservations")}
    assert {"deposit", "client_category", "duration_type", "extras_json"} <= cols
    with engine.connect() as conn:
        assert conn.execute(text("SELECT amount, deposit FROM reservations")).one() == (5000000, 0)


def test_assistant_tools_use_the_same_tariffs(client, customer):
    from app.assistant.client_router import TOOLS, _make_executor
    from app.database import SessionLocal
    from app.models import User

    assert {t["name"] for t in TOOLS} >= {"check_availability", "get_quote", "create_reservation", "list_my_reservations"}
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "client.tarifs@gmail.com").one()
        run = _make_executor(db, user)
        import json
        text_, is_error = run("get_quote", {"room": "salle_reunion", "start_time": "08:00", "end_time": "13:00",
                                           "client_category": "partenaire_prive", "extras": [{"key": "sonorisation_complete", "quantity": 1}]})
        data = json.loads(text_)
        assert not is_error
        assert data["rental_fcfa"] == 2_000_000 and data["total_to_pay_fcfa"] == 2_000_000 + 350_000 + 500_000
        text_, is_error = run("get_quote", {"room": "gymnase", "start_time": "08:00", "end_time": "13:00", "client_category": "nimporte"})
        assert is_error
    finally:
        db.close()
