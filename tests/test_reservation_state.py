from decimal import Decimal

import pytest

from conftest import MONDAY, at
from pitch_booking.domain.errors import InvalidStateTransitionError
from pitch_booking.domain.reservation import Reservation, ReservationStatus


@pytest.fixture
def reservation() -> Reservation:
    return Reservation(
        id=1,
        pitch_id=1,
        customer_email="ali@example.com",
        start=at(MONDAY, 20),
        hours=1,
        price=Decimal("1300"),
    )


def test_new_reservation_is_pending(reservation):
    assert reservation.status is ReservationStatus.PENDING
    assert reservation.is_active


def test_pending_to_confirmed(reservation):
    reservation.confirm("TX-1")
    assert reservation.status is ReservationStatus.CONFIRMED
    assert reservation.payment_reference == "TX-1"


def test_pending_to_cancelled(reservation):
    reservation.cancel()
    assert reservation.status is ReservationStatus.CANCELLED


def test_confirmed_to_cancelled(reservation):
    reservation.confirm("TX-1")
    reservation.cancel()
    assert reservation.status is ReservationStatus.CANCELLED


def test_confirmed_cannot_be_confirmed_again(reservation):
    reservation.confirm("TX-1")
    with pytest.raises(InvalidStateTransitionError):
        reservation.confirm("TX-2")
    assert reservation.payment_reference == "TX-1"


def test_cancelled_cannot_be_confirmed(reservation):
    reservation.cancel()
    with pytest.raises(InvalidStateTransitionError):
        reservation.ensure_can_confirm()
    with pytest.raises(InvalidStateTransitionError):
        reservation.confirm("TX-1")
    assert reservation.status is ReservationStatus.CANCELLED


def test_cancelled_cannot_be_cancelled_again(reservation):
    reservation.cancel()
    with pytest.raises(InvalidStateTransitionError):
        reservation.cancel()


def test_cancelled_reservation_no_longer_blocks_its_slot(reservation):
    assert reservation.overlaps(reservation.start, reservation.end)
    reservation.cancel()
    assert not reservation.is_active
    assert not reservation.overlaps(reservation.start, reservation.end)
