from datetime import datetime
from decimal import Decimal

import pytest

from pitch_booking.application.reservation_service import ReservationService
from pitch_booking.domain.models import Pitch


@pytest.fixture
def service() -> ReservationService:
    s = ReservationService()
    s.add_pitch(Pitch(id=1, name="Arena 1", owner_id=10, hourly_price=Decimal("1000")))
    return s


def test_weekday_morning_uses_base_price(service):
    r = service.create_reservation(1, "a@b.com", datetime(2026, 11, 2, 10))
    assert r.price == Decimal("1000")


def test_double_booking_is_rejected(service):
    service.create_reservation(1, "a@b.com", datetime(2026, 11, 2, 20))
    with pytest.raises(ValueError):
        service.create_reservation(1, "c@d.com", datetime(2026, 11, 2, 20))


def test_pay_then_cancel(service):
    r = service.create_reservation(1, "a@b.com", datetime(2026, 11, 2, 20))
    service.pay(r.id, "4111111111111111")
    assert r.status == "CONFIRMED"
    service.cancel(r.id)
    assert r.status == "CANCELLED"
