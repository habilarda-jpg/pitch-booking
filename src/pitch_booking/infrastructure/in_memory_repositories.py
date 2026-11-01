from itertools import count

from pitch_booking.application.ports import PitchRepository, ReservationRepository
from pitch_booking.domain.errors import NotFoundError
from pitch_booking.domain.pitch import Pitch
from pitch_booking.domain.reservation import Reservation


class InMemoryPitchRepository(PitchRepository):
    def __init__(self) -> None:
        self._items: dict[int, Pitch] = {}
        self._ids = count(1)

    def next_id(self) -> int:
        return next(self._ids)

    def save(self, pitch: Pitch) -> None:
        self._items[pitch.id] = pitch

    def get(self, pitch_id: int) -> Pitch:
        try:
            return self._items[pitch_id]
        except KeyError:
            raise NotFoundError(f"Pitch {pitch_id} not found") from None

    def list_all(self) -> list[Pitch]:
        return list(self._items.values())


class InMemoryReservationRepository(ReservationRepository):
    def __init__(self) -> None:
        self._items: dict[int, Reservation] = {}
        self._ids = count(1)

    def next_id(self) -> int:
        return next(self._ids)

    def save(self, reservation: Reservation) -> None:
        self._items[reservation.id] = reservation

    def get(self, reservation_id: int) -> Reservation:
        try:
            return self._items[reservation_id]
        except KeyError:
            raise NotFoundError(f"Reservation {reservation_id} not found") from None

    def list_for_pitch(self, pitch_id: int) -> list[Reservation]:
        return [r for r in self._items.values() if r.pitch_id == pitch_id]
