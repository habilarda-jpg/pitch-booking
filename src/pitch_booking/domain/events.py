from dataclasses import dataclass

from pitch_booking.domain.reservation import Reservation


@dataclass(frozen=True)
class ReservationEvent:
    reservation: Reservation


@dataclass(frozen=True)
class ReservationCreated(ReservationEvent):
    pass


@dataclass(frozen=True)
class ReservationConfirmed(ReservationEvent):
    pass


@dataclass(frozen=True)
class ReservationCancelled(ReservationEvent):
    pass
