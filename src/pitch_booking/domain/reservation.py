from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import StrEnum

from pitch_booking.domain.errors import InvalidStateTransitionError


class ReservationStatus(StrEnum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class ReservationState:
    status: ReservationStatus
    blocks_slot: bool = True

    def ensure_can_confirm(self) -> None:
        raise InvalidStateTransitionError(f"Cannot confirm a {self.status} reservation")

    def ensure_can_cancel(self) -> None:
        raise InvalidStateTransitionError(f"Cannot cancel a {self.status} reservation")

    def confirm(self) -> ReservationState:
        self.ensure_can_confirm()
        return ConfirmedState()

    def cancel(self) -> ReservationState:
        self.ensure_can_cancel()
        return CancelledState()


class PendingState(ReservationState):
    status = ReservationStatus.PENDING

    def ensure_can_confirm(self) -> None:
        pass

    def ensure_can_cancel(self) -> None:
        pass


class ConfirmedState(ReservationState):
    status = ReservationStatus.CONFIRMED

    def ensure_can_cancel(self) -> None:
        pass


class CancelledState(ReservationState):
    status = ReservationStatus.CANCELLED
    blocks_slot = False


@dataclass
class Reservation:
    id: int
    pitch_id: int
    customer_email: str
    start: datetime
    hours: int
    price: Decimal
    payment_reference: str | None = None
    _state: ReservationState = field(default_factory=PendingState, repr=False)

    @property
    def status(self) -> ReservationStatus:
        return self._state.status

    @property
    def end(self) -> datetime:
        return self.start + timedelta(hours=self.hours)

    @property
    def is_active(self) -> bool:
        return self._state.blocks_slot

    def overlaps(self, start: datetime, end: datetime) -> bool:
        return self.is_active and start < self.end and self.start < end

    def ensure_can_confirm(self) -> None:
        self._state.ensure_can_confirm()

    def confirm(self, payment_reference: str) -> None:
        self._state = self._state.confirm()
        self.payment_reference = payment_reference

    def cancel(self) -> None:
        self._state = self._state.cancel()
