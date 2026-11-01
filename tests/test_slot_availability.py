from datetime import timedelta
from decimal import Decimal

import pytest

from conftest import MONDAY, at
from pitch_booking.domain.errors import InvalidReservationError, SlotUnavailableError


def slots_by_hour(container, pitch):
    slots = container.availability_service.slots_for_day(pitch.id, MONDAY.date())
    return {s.start.hour: s for s in slots}


def test_empty_day_has_all_hourly_slots_available(container, pitch):
    slots = slots_by_hour(container, pitch)
    assert sorted(slots) == list(range(9, 24))
    assert all(s.available for s in slots.values())
    assert slots[23].end == at(MONDAY, 0) + timedelta(days=1)


def test_slots_show_price_for_that_hour(container, pitch):
    slots = slots_by_hour(container, pitch)
    assert slots[10].price == Decimal("1000.00")
    assert slots[20].price == Decimal("1300.00")


def test_booked_hours_become_unavailable(container, pitch):
    container.reservation_service.create_reservation(pitch.id, "a@b.com", at(MONDAY, 19), hours=2)
    slots = slots_by_hour(container, pitch)
    assert [h for h, s in slots.items() if not s.available] == [19, 20]


def test_cancelling_frees_the_slot(container, pitch):
    r = container.reservation_service.create_reservation(pitch.id, "a@b.com", at(MONDAY, 19))
    container.reservation_service.cancel(r.id)
    assert slots_by_hour(container, pitch)[19].available


def test_overlapping_reservation_is_rejected(container, pitch):
    container.reservation_service.create_reservation(pitch.id, "a@b.com", at(MONDAY, 19), hours=2)
    with pytest.raises(SlotUnavailableError):
        container.reservation_service.create_reservation(pitch.id, "c@d.com", at(MONDAY, 20))


def test_adjacent_reservations_are_allowed(container, pitch):
    container.reservation_service.create_reservation(pitch.id, "a@b.com", at(MONDAY, 19))
    r = container.reservation_service.create_reservation(pitch.id, "c@d.com", at(MONDAY, 20))
    assert r.start == at(MONDAY, 20)


def test_same_hour_on_another_pitch_is_independent(container, pitch):
    other = container.pitch_service.register_pitch("Arena 2", owner_id=10, hourly_price=Decimal("900"))
    container.reservation_service.create_reservation(pitch.id, "a@b.com", at(MONDAY, 19))
    r = container.reservation_service.create_reservation(other.id, "c@d.com", at(MONDAY, 19))
    assert r.pitch_id == other.id


@pytest.mark.parametrize(
    ("start", "hours"),
    [
        (at(MONDAY, 8), 1),
        (at(MONDAY, 23), 2),
        (at(MONDAY, 19).replace(minute=30), 1),
        (at(MONDAY, 19), 0),
        (at(MONDAY, 12), 4),
    ],
)
def test_invalid_slots_are_rejected(container, pitch, start, hours):
    with pytest.raises(InvalidReservationError):
        container.reservation_service.create_reservation(pitch.id, "a@b.com", start, hours)
