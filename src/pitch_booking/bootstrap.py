from dataclasses import dataclass
from decimal import Decimal

from pitch_booking.application.availability_service import AvailabilityService
from pitch_booking.application.event_publisher import EventPublisher
from pitch_booking.application.pitch_service import PitchService
from pitch_booking.application.reservation_service import ReservationService
from pitch_booking.domain.factories import ReservationFactory, SlotFactory
from pitch_booking.domain.pricing import PriceCalculator
from pitch_booking.infrastructure.fakebank_sdk import FakeBankClient
from pitch_booking.infrastructure.in_memory_repositories import (
    InMemoryPitchRepository,
    InMemoryReservationRepository,
)
from pitch_booking.infrastructure.notifications import AuditLog, EmailNotifier
from pitch_booking.infrastructure.payment_adapter import FakeBankPaymentAdapter


@dataclass
class Container:
    pitch_service: PitchService
    reservation_service: ReservationService
    availability_service: AvailabilityService
    email_notifier: EmailNotifier
    audit_log: AuditLog
    bank: FakeBankClient


def build_container(seed: bool = False) -> Container:
    pitches = InMemoryPitchRepository()
    reservations = InMemoryReservationRepository()
    calculator = PriceCalculator()
    bank = FakeBankClient()

    email_notifier = EmailNotifier()
    audit_log = AuditLog()
    publisher = EventPublisher()
    publisher.subscribe(email_notifier)
    publisher.subscribe(audit_log)

    pitch_service = PitchService(pitches)
    container = Container(
        pitch_service=pitch_service,
        reservation_service=ReservationService(
            pitches,
            reservations,
            ReservationFactory(calculator),
            FakeBankPaymentAdapter(bank),
            publisher,
        ),
        availability_service=AvailabilityService(pitches, reservations, SlotFactory(calculator)),
        email_notifier=email_notifier,
        audit_log=audit_log,
        bank=bank,
    )
    if seed:
        pitch_service.register_pitch("Kadıköy Arena", owner_id=1, hourly_price=Decimal("1200"))
        pitch_service.register_pitch("Beşiktaş Halı Saha", owner_id=2, hourly_price=Decimal("1000"))
    return container
