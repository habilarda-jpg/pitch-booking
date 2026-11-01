from datetime import datetime

from pitch_booking.application.event_publisher import EventPublisher
from pitch_booking.application.ports import (
    PaymentGateway,
    PitchRepository,
    ReservationRepository,
)
from pitch_booking.domain.errors import SlotUnavailableError
from pitch_booking.domain.events import (
    ReservationCancelled,
    ReservationConfirmed,
    ReservationCreated,
)
from pitch_booking.domain.factories import ReservationFactory
from pitch_booking.domain.reservation import Reservation


class ReservationService:
    def __init__(
        self,
        pitches: PitchRepository,
        reservations: ReservationRepository,
        factory: ReservationFactory,
        payment_gateway: PaymentGateway,
        publisher: EventPublisher,
    ) -> None:
        self._pitches = pitches
        self._reservations = reservations
        self._factory = factory
        self._payment_gateway = payment_gateway
        self._publisher = publisher

    def create_reservation(
        self, pitch_id: int, customer_email: str, start: datetime, hours: int = 1
    ) -> Reservation:
        pitch = self._pitches.get(pitch_id)
        reservation = self._factory.create(
            self._reservations.next_id(), pitch, customer_email, start, hours
        )
        existing = self._reservations.list_for_pitch(pitch_id)
        if any(r.overlaps(reservation.start, reservation.end) for r in existing):
            raise SlotUnavailableError("Slot already booked")
        self._reservations.save(reservation)
        self._publisher.publish(ReservationCreated(reservation))
        return reservation

    def get_reservation(self, reservation_id: int) -> Reservation:
        return self._reservations.get(reservation_id)

    def pay(self, reservation_id: int, card_number: str) -> Reservation:
        reservation = self._reservations.get(reservation_id)
        reservation.ensure_can_confirm()
        transaction_id = self._payment_gateway.charge(
            reservation.price, card_number, f"reservation-{reservation.id}"
        )
        reservation.confirm(transaction_id)
        self._reservations.save(reservation)
        self._publisher.publish(ReservationConfirmed(reservation))
        return reservation

    def cancel(self, reservation_id: int) -> Reservation:
        reservation = self._reservations.get(reservation_id)
        reservation.cancel()
        self._reservations.save(reservation)
        self._publisher.publish(ReservationCancelled(reservation))
        return reservation
