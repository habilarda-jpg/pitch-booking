from datetime import date

from pitch_booking.application.ports import PitchRepository, ReservationRepository
from pitch_booking.domain.factories import SlotFactory
from pitch_booking.domain.slot import Slot


class AvailabilityService:
    def __init__(
        self,
        pitches: PitchRepository,
        reservations: ReservationRepository,
        slot_factory: SlotFactory,
    ) -> None:
        self._pitches = pitches
        self._reservations = reservations
        self._slot_factory = slot_factory

    def slots_for_day(self, pitch_id: int, day: date) -> list[Slot]:
        pitch = self._pitches.get(pitch_id)
        booked = self._reservations.list_for_pitch(pitch_id)
        return [
            self._slot_factory.as_unavailable(slot)
            if any(r.overlaps(slot.start, slot.end) for r in booked)
            else slot
            for slot in self._slot_factory.create_for_day(pitch, day)
        ]
