from dataclasses import dataclass

from pitch_booking.application.ports import ReservationObserver
from pitch_booking.domain.events import (
    ReservationCancelled,
    ReservationConfirmed,
    ReservationCreated,
    ReservationEvent,
)


@dataclass(frozen=True)
class Email:
    to: str
    subject: str
    body: str


class EmailNotifier(ReservationObserver):
    SUBJECTS = {
        ReservationCreated: "Reservation received - awaiting payment",
        ReservationConfirmed: "Reservation confirmed",
        ReservationCancelled: "Reservation cancelled",
    }

    def __init__(self) -> None:
        self.outbox: list[Email] = []

    def notify(self, event: ReservationEvent) -> None:
        r = event.reservation
        subject = self.SUBJECTS.get(type(event), "Reservation update")
        body = (
            f"Reservation #{r.id}: pitch {r.pitch_id}, {r.start:%Y-%m-%d %H:%M}, "
            f"{r.hours}h, {r.price} TL, status {r.status}"
        )
        self.outbox.append(Email(to=r.customer_email, subject=subject, body=body))


class AuditLog(ReservationObserver):
    def __init__(self) -> None:
        self.entries: list[str] = []

    def notify(self, event: ReservationEvent) -> None:
        self.entries.append(f"{type(event).__name__} reservation={event.reservation.id}")
