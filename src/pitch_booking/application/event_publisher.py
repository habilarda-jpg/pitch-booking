from pitch_booking.application.ports import ReservationObserver
from pitch_booking.domain.events import ReservationEvent


class EventPublisher:
    def __init__(self) -> None:
        self._observers: list[ReservationObserver] = []

    def subscribe(self, observer: ReservationObserver) -> None:
        self._observers.append(observer)

    def unsubscribe(self, observer: ReservationObserver) -> None:
        self._observers.remove(observer)

    def publish(self, event: ReservationEvent) -> None:
        for observer in self._observers:
            observer.notify(event)
