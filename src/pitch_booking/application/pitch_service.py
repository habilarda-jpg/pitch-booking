from decimal import Decimal

from pitch_booking.application.ports import PitchRepository
from pitch_booking.domain.errors import InvalidReservationError
from pitch_booking.domain.pitch import Pitch


class PitchService:
    def __init__(self, pitches: PitchRepository) -> None:
        self._pitches = pitches

    def register_pitch(self, name: str, owner_id: int, hourly_price: Decimal) -> Pitch:
        if hourly_price <= 0:
            raise InvalidReservationError("Hourly price must be positive")
        pitch = Pitch(
            id=self._pitches.next_id(), name=name, owner_id=owner_id, hourly_price=hourly_price
        )
        self._pitches.save(pitch)
        return pitch

    def change_price(self, pitch_id: int, owner_id: int, new_price: Decimal) -> Pitch:
        pitch = self._pitches.get(pitch_id)
        pitch.change_price(owner_id, new_price)
        self._pitches.save(pitch)
        return pitch

    def get_pitch(self, pitch_id: int) -> Pitch:
        return self._pitches.get(pitch_id)

    def list_pitches(self) -> list[Pitch]:
        return self._pitches.list_all()
