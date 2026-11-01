# Refactor 001 – Split the "God" `ReservationService`

| | |
|---|---|
| **Module** | M2 – SOLID principles |
| **Main principle fixed** | **S**ingle Responsibility Principle (SRP) |
| **Also improved** | **D**ependency Inversion (DIP), **O**pen/Closed (OCP) |
| **Before** | commit *"Naive ReservationService (pre-refactor baseline)"* |
| **After** | `src/pitch_booking/application/reservation_service.py` and the files listed below |

## 1. Problem

The first version of `ReservationService` was written deliberately naive. One class did
**six** different jobs:

| Responsibility | Reason it might change |
|---|---|
| Storing pitches and reservations in its own `dict`s | Moving to PostgreSQL |
| Checking slot overlap | New booking rules |
| Computing prices with `if/elif` | Business adds a "holiday" or "student" tariff |
| Calling the bank directly | Switching payment provider |
| Changing status with raw strings | Adding a new lifecycle state |
| Building and "sending" e-mails | Adding SMS / push notifications |

SRP says *a class should have only one reason to change*. This class had six, so every
change, however small, meant editing (and re-testing) the same file. It could not be
unit-tested without also touching storage, payment and notifications.

## 2. Before

```python
class ReservationService:
    def __init__(self) -> None:
        self.pitches: dict[int, Pitch] = {}
        self.reservations: dict[int, Reservation] = {}
        self._next_id = 1
        self.sent_emails: list[str] = []

    def create_reservation(self, pitch_id, customer_email, start, hours=1):
        ...
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

        reservation = Reservation(id=self._next_id, ..., price=price)
        self.reservations[reservation.id] = reservation
        self._next_id += 1

        self.sent_emails.append(f"To: {customer_email} | Your reservation ...")
        print(f"[EMAIL] sent to {customer_email}")
        return reservation

    def pay(self, reservation_id, card_number):
        reservation = self.reservations[reservation_id]
        if reservation.status != "PENDING":
            raise ValueError(...)
        if not card_number.startswith("4") or len(card_number) != 16:
            raise ValueError("Payment declined")
        print(f"[FAKEBANK] charged {reservation.price} TL")
        reservation.status = "CONFIRMED"
        self.sent_emails.append(...)
        return reservation
```

## 3. After

Each responsibility now lives in its own class. `ReservationService` only **orchestrates**
the use case, and it depends on **abstractions** (ports) that are injected, not on concrete
classes.

```python
class ReservationService:
    def __init__(
        self,
        pitches: PitchRepository,
        reservations: ReservationRepository,
        factory: ReservationFactory,
        payment_gateway: PaymentGateway,
        publisher: EventPublisher,
    ) -> None:
        ...

    def create_reservation(self, pitch_id, customer_email, start, hours=1):
        pitch = self._pitches.get(pitch_id)
        reservation = self._factory.create(
            self._reservations.next_id(), pitch, customer_email, start, hours
        )
        existing = self._reservations.list_for_pitch(pitch_id)
        if any(r.overlaps(reservation.start, reservation.end) for r in existing):
            raise SlotUnavailableError("Slot already booked")
        self._reservations.save(reservation)
        self._publisher.publish(ReservationCreated(reservation))
        return reservation

    def pay(self, reservation_id, card_number):
        reservation = self._reservations.get(reservation_id)
        reservation.ensure_can_confirm()
        transaction_id = self._payment_gateway.charge(
            reservation.price, card_number, f"reservation-{reservation.id}"
        )
        reservation.confirm(transaction_id)
        self._reservations.save(reservation)
        self._publisher.publish(ReservationConfirmed(reservation))
        return reservation
```

| Responsibility | New home | Pattern |
|---|---|---|
| Persistence | `PitchRepository` / `ReservationRepository` ports, with `InMemory*Repository` implementations (`infrastructure/in_memory_repositories.py`) | Repository |
| Building a valid reservation and pricing it | `ReservationFactory` (`domain/factories.py`) | Factory |
| Pricing rules | `PricingStrategy` + `PriceCalculator` (`domain/pricing.py`) | Strategy |
| Payment provider | `PaymentGateway` port, with `FakeBankPaymentAdapter` (`infrastructure/payment_adapter.py`) | Adapter |
| Lifecycle / allowed transitions | `PendingState` / `ConfirmedState` / `CancelledState` (`domain/reservation.py`) | State |
| Notifications | `EventPublisher` + `EmailNotifier`, `AuditLog` observers | Observer |
| Overlap rule | `Reservation.overlaps()` (domain entity) | — |

## 4. Which principles this fixes

- **SRP:** each class above has one reason to change. Changing tariffs touches only
  `pricing.py`. Changing the bank touches only the adapter.
- **DIP:** the application layer depends on `PaymentGateway`, `ReservationRepository` and
  `ReservationObserver`, which are interfaces defined in `application/ports.py`.
  Infrastructure implements them, and they are wired together in one place,
  `bootstrap.py`. High-level policy no longer depends on low-level details.
- **OCP:** you can add a new tariff (see `test_new_strategy_can_be_added_without_changing_calculator`)
  or a new notification channel (a new observer) by **adding** a class rather than
  editing existing code.

## 5. Consequences

- More files and classes. That is acceptable, because each one is small and easy to read.
- Tests are now fast and isolated. The service tests check the observer outbox and the
  fake bank's transaction list, with no printing and no hidden state.
- A bug fixed along the way: the naive `pay()` could have charged the card and *then*
  failed the status check. The new code calls `ensure_can_confirm()` **before** charging
  (`test_paying_cancelled_reservation_never_reaches_the_bank`).
