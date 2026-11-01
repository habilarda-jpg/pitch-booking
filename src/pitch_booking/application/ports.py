from abc import ABC, abstractmethod
from decimal import Decimal

from pitch_booking.domain.events import ReservationEvent
from pitch_booking.domain.pitch import Pitch
from pitch_booking.domain.reservation import Reservation


class PitchRepository(ABC):
    @abstractmethod
    def next_id(self) -> int: ...

    @abstractmethod
    def save(self, pitch: Pitch) -> None: ...

    @abstractmethod
    def get(self, pitch_id: int) -> Pitch: ...

    @abstractmethod
    def list_all(self) -> list[Pitch]: ...


class ReservationRepository(ABC):
    @abstractmethod
    def next_id(self) -> int: ...

    @abstractmethod
    def save(self, reservation: Reservation) -> None: ...

    @abstractmethod
    def get(self, reservation_id: int) -> Reservation: ...

    @abstractmethod
    def list_for_pitch(self, pitch_id: int) -> list[Reservation]: ...


class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, amount: Decimal, card_number: str, reference: str) -> str: ...


class ReservationObserver(ABC):
    @abstractmethod
    def notify(self, event: ReservationEvent) -> None: ...
