import pytest
from fastapi.testclient import TestClient

from pitch_booking.api.app import create_app
from pitch_booking.bootstrap import build_container


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app(build_container(seed=True)))


def test_full_booking_flow(client):
    pitches = client.get("/pitches").json()
    assert len(pitches) == 2
    pitch_id = pitches[0]["id"]

    slots = client.get(f"/pitches/{pitch_id}/slots", params={"day": "2026-11-02"}).json()
    assert all(s["available"] for s in slots)

    created = client.post(
        "/reservations",
        json={"pitch_id": pitch_id, "customer_email": "a@b.com", "start": "2026-11-02T20:00:00"},
    )
    assert created.status_code == 201
    reservation = created.json()
    assert reservation["status"] == "PENDING"
    assert float(reservation["price"]) == 1560.0

    paid = client.post(f"/reservations/{reservation['id']}/pay", json={"card_number": "4242424242424242"})
    assert paid.json()["status"] == "CONFIRMED"

    slots = client.get(f"/pitches/{pitch_id}/slots", params={"day": "2026-11-02"}).json()
    assert [s["available"] for s in slots if s["start"].endswith("20:00:00")] == [False]

    cancelled = client.post(f"/reservations/{reservation['id']}/cancel")
    assert cancelled.json()["status"] == "CANCELLED"


def test_domain_errors_map_to_http_status_codes(client):
    body = {"pitch_id": 1, "customer_email": "a@b.com", "start": "2026-11-02T20:00:00"}
    first = client.post("/reservations", json=body).json()
    assert client.post("/reservations", json=body).status_code == 409
    assert client.get("/reservations/999").status_code == 404
    assert (
        client.post(f"/reservations/{first['id']}/pay", json={"card_number": "4000000000000002"}).status_code
        == 402
    )
    assert client.patch("/pitches/1/price", json={"owner_id": 99, "hourly_price": "10"}).status_code == 403
    assert client.post("/reservations", json={**body, "start": "2026-11-02T05:00:00"}).status_code == 400


def test_owner_creates_pitch_and_changes_price(client):
    created = client.post("/pitches", json={"name": "Yeni Saha", "owner_id": 7, "hourly_price": "800"})
    assert created.status_code == 201
    pitch_id = created.json()["id"]
    updated = client.patch(f"/pitches/{pitch_id}/price", json={"owner_id": 7, "hourly_price": "900"})
    assert float(updated.json()["hourly_price"]) == 900.0
