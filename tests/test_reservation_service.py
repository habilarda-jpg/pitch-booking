from decimal import Decimal

import pytest

from conftest import MONDAY, at
from pitch_booking.domain.errors import (
    InvalidStateTransitionError,
    NotFoundError,
    PaymentDeclinedError,
    PermissionDeniedError,
)
from pitch_booking.domain.reservation import ReservationStatus

GOOD_CARD = "4242424242424242"
DECLINED_CARD = "4000000000000002"


@pytest.fixture
def reservation(container, pitch):
    return container.reservation_service.create_reservation(pitch.id, "ali@example.com", at(MONDAY, 20))


def test_create_reservation_prices_it_and_notifies_observers(container, reservation):
    assert reservation.price == Decimal("1300.00")
    assert reservation.status is ReservationStatus.PENDING
    assert container.email_notifier.outbox[-1].to == "ali@example.com"
    assert container.audit_log.entries == [f"ReservationCreated reservation={reservation.id}"]


def test_pay_charges_through_adapter_and_confirms(container, reservation):
    container.reservation_service.pay(reservation.id, GOOD_CARD)
    assert reservation.status is ReservationStatus.CONFIRMED
    assert reservation.payment_reference == container.bank.transactions[0]["txn_id"]
    assert container.bank.transactions[0]["amount_kurus"] == 130000
    assert container.email_notifier.outbox[-1].subject == "Reservation confirmed"


def test_declined_payment_keeps_reservation_pending(container, reservation):
    with pytest.raises(PaymentDeclinedError):
        container.reservation_service.pay(reservation.id, DECLINED_CARD)
    assert reservation.status is ReservationStatus.PENDING
    assert container.bank.transactions == []


def test_paying_cancelled_reservation_never_reaches_the_bank(container, reservation):
    container.reservation_service.cancel(reservation.id)
    with pytest.raises(InvalidStateTransitionError):
        container.reservation_service.pay(reservation.id, GOOD_CARD)
    assert container.bank.transactions == []


def test_cancel_publishes_event(container, reservation):
    container.reservation_service.cancel(reservation.id)
    assert container.audit_log.entries[-1] == f"ReservationCancelled reservation={reservation.id}"
    assert container.email_notifier.outbox[-1].subject == "Reservation cancelled"


def test_unknown_ids_raise_not_found(container, pitch):
    with pytest.raises(NotFoundError):
        container.reservation_service.create_reservation(999, "a@b.com", at(MONDAY, 10))
    with pytest.raises(NotFoundError):
        container.reservation_service.pay(999, GOOD_CARD)


def test_only_owner_can_change_price(container, pitch):
    with pytest.raises(PermissionDeniedError):
        container.pitch_service.change_price(pitch.id, owner_id=99, new_price=Decimal("1"))
    container.pitch_service.change_price(pitch.id, owner_id=10, new_price=Decimal("1500"))
    r = container.reservation_service.create_reservation(pitch.id, "a@b.com", at(MONDAY, 10))
    assert r.price == Decimal("1500.00")
