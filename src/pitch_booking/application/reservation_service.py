from datetime import datetime, timedelta
from decimal import Decimal

from pitch_booking.domain.models import Pitch, Reservation


class ReservationService:
    def __init__(self) -> None:
        self.pitches: dict[int, Pitch] = {}
        self.reservations: dict[int, Reservation] = {}
        self._next_id = 1
        self.sent_emails: list[str] = []

    def add_pitch(self, pitch: Pitch) -> None:
        self.pitches[pitch.id] = pitch

    def create_reservation(
        self, pitch_id: int, customer_email: str, start: datetime, hours: int = 1
    ) -> Reservation:
        if pitch_id not in self.pitches:
            raise ValueError("Pitch not found")
        if start.minute != 0 or start.second != 0:
            raise ValueError("Reservations must start on the hour")
        pitch = self.pitches[pitch_id]

        end = start + timedelta(hours=hours)
        for r in self.reservations.values():
            if r.pitch_id == pitch_id and r.status != "CANCELLED":
                if start < r.end and r.start < end:
                    raise ValueError("Slot already booked")

        price = Decimal("0")
        for h in range(hours):
            t = start + timedelta(hours=h)
            if t.weekday() >= 5:
                price += pitch.hourly_price * Decimal("1.5")
            elif 18 <= t.hour < 24:
                price += pitch.hourly_price * Decimal("1.3")
            else:
                price += pitch.hourly_price

        reservation = Reservation(
            id=self._next_id,
            pitch_id=pitch_id,
            customer_email=customer_email,
            start=start,
            hours=hours,
            price=price,
        )
        self.reservations[reservation.id] = reservation
        self._next_id += 1

        self.sent_emails.append(
            f"To: {customer_email} | Your reservation #{reservation.id} at "
            f"{pitch.name} on {start:%Y-%m-%d %H:%M} is pending. Price: {price} TL"
        )
        print(f"[EMAIL] sent to {customer_email}")
        return reservation

    def pay(self, reservation_id: int, card_number: str) -> Reservation:
        reservation = self.reservations[reservation_id]
        if reservation.status != "PENDING":
            raise ValueError(f"Cannot pay a {reservation.status} reservation")

        if not card_number.startswith("4") or len(card_number) != 16:
            raise ValueError("Payment declined")
        print(f"[FAKEBANK] charged {reservation.price} TL")

        reservation.status = "CONFIRMED"
        self.sent_emails.append(
            f"To: {reservation.customer_email} | Reservation #{reservation.id} confirmed."
        )
        return reservation

    def cancel(self, reservation_id: int) -> Reservation:
        reservation = self.reservations[reservation_id]
        if reservation.status == "CANCELLED":
            raise ValueError("Reservation already cancelled")
        reservation.status = "CANCELLED"
        self.sent_emails.append(
            f"To: {reservation.customer_email} | Reservation #{reservation.id} cancelled."
        )
        return reservation
