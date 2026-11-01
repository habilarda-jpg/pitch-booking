from dataclasses import replace
from datetime import date, datetime, time, timedelta

from pitch_booking.domain.errors import InvalidReservationError
from pitch_booking.domain.pitch import Pitch
from pitch_booking.domain.pricing import PriceCalculator
from pitch_booking.domain.reservation import Reservation
from pitch_booking.domain.slot import OpeningHours, Slot


class SlotFactory:
    def __init__(
        self, calculator: PriceCalculator, opening_hours: OpeningHours = OpeningHours()
    ) -> None:
        self._calculator = calculator
        self._opening_hours = opening_hours

    def create_for_day(self, pitch: Pitch, day: date) -> list[Slot]:
        first = datetime.combine(day, time()) + timedelta(hours=self._opening_hours.open_hour)
        count = self._opening_hours.close_hour - self._opening_hours.open_hour
        starts = [first + timedelta(hours=i) for i in range(count)]
        return [
            Slot(pitch_id=pitch.id, start=s, price=self._calculator.hourly_price(pitch, s))
            for s in starts
        ]

    @staticmethod
    def as_unavailable(slot: Slot) -> Slot:
        return replace(slot, available=False)


class ReservationFactory:
    MAX_HOURS = 3

    def __init__(
        self, calculator: PriceCalculator, opening_hours: OpeningHours = OpeningHours()
    ) -> None:
        self._calculator = calculator
        self._opening_hours = opening_hours

    def create(
        self,
        reservation_id: int,
        pitch: Pitch,
        customer_email: str,
        start: datetime,
        hours: int,
    ) -> Reservation:
        if "@" not in customer_email:
            raise InvalidReservationError("A valid customer e-mail is required")
        if start.minute or start.second or start.microsecond:
            raise InvalidReservationError("Reservations must start on the hour")
        if not 1 <= hours <= self.MAX_HOURS:
            raise InvalidReservationError(f"Reservations must last 1 to {self.MAX_HOURS} hours")
        if not self._opening_hours.contains(start, hours):
            raise InvalidReservationError("Reservation is outside opening hours")
        return Reservation(
            id=reservation_id,
            pitch_id=pitch.id,
            customer_email=customer_email,
            start=start,
            hours=hours,
            price=self._calculator.total(pitch, start, hours),
        )
