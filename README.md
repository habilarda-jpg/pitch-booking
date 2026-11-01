# Pitch Booking – Halı Saha Rezervasyon Sistemi

Course project for **Software Design and Architecture**, Sprint A (Modules 1–5).

A small reservation system for football pitches:

- **Customers** browse pitches, see free hourly slots with their prices, create a
  reservation, pay (mock bank) and cancel.
- **Pitch owners** register pitches and change their hourly price.

Pricing: weekday 09–18 = base price · weekday 18–24 = base × 1.3 (peak) · weekend = base × 1.5.
Opening hours are 09:00–24:00, and a reservation is 1–3 whole hours long.
Lifecycle: `PENDING → CONFIRMED → CANCELLED` (or `PENDING → CANCELLED`).

Tech: Python 3.12, [uv](https://docs.astral.sh/uv/), FastAPI, pytest. There is no
real database yet; all data is in memory and is lost on restart.

## How to run

```bash
uv sync
uv run uvicorn pitch_booking.api.app:app --reload
```

Open <http://127.0.0.1:8000/docs> for the interactive Swagger UI. Two demo pitches are
seeded on startup.

| Method | Path | Purpose |
|---|---|---|
| GET | `/pitches` | List pitches |
| POST | `/pitches` | Owner registers a pitch |
| PATCH | `/pitches/{id}/price` | Owner changes the hourly price |
| GET | `/pitches/{id}/slots?day=2026-11-02` | Hourly slots, prices and availability |
| POST | `/reservations` | Create a reservation (status `PENDING`) |
| GET | `/reservations/{id}` | Reservation details |
| POST | `/reservations/{id}/pay` | Pay with the mock bank, which sets status `CONFIRMED` |
| POST | `/reservations/{id}/cancel` | Cancel (status `CANCELLED`, slot becomes free again) |

Mock bank test cards: `4242424242424242` is approved and `4000000000000002` is declined
(any 16-digit card ending in `0002` is declined).

Example:

```bash
curl -X POST localhost:8000/reservations -H "Content-Type: application/json" \
  -d '{"pitch_id": 1, "customer_email": "ali@example.com", "start": "2026-11-02T20:00:00", "hours": 1}'
curl -X POST localhost:8000/reservations/1/pay -H "Content-Type: application/json" \
  -d '{"card_number": "4242424242424242"}'
```

## How to test

```bash
uv run pytest
```

| Test file | Covers |
|---|---|
| `tests/test_pricing.py` | Normal / peak / weekend strategies, multi-hour totals, adding a new strategy (OCP) |
| `tests/test_reservation_state.py` | All valid and invalid state transitions |
| `tests/test_slot_availability.py` | Daily slots, booked or cancelled slots, overlap, opening-hours validation |
| `tests/test_reservation_service.py` | Use cases, payment adapter, observers, owner-only price change |
| `tests/test_api.py` | End-to-end HTTP flow and error → status-code mapping |

## Project structure

```
src/pitch_booking/
├── domain/            entities and business rules, no framework imports
│   ├── pitch.py           Pitch entity (owner-only price change)
│   ├── reservation.py     Reservation entity + State pattern
│   ├── pricing.py         Strategy pattern + PriceCalculator
│   ├── slot.py            Slot value object, OpeningHours
│   ├── factories.py       SlotFactory, ReservationFactory
│   ├── events.py          ReservationCreated / Confirmed / Cancelled
│   └── errors.py          Domain exceptions
├── application/       use cases + ports (interfaces)
│   ├── ports.py           Repository, PaymentGateway, ReservationObserver interfaces
│   ├── reservation_service.py
│   ├── availability_service.py
│   ├── pitch_service.py
│   └── event_publisher.py Observer subject
├── infrastructure/    adapters that implement the ports
│   ├── in_memory_repositories.py
│   ├── fakebank_sdk.py    pretend third-party payment SDK
│   ├── payment_adapter.py Adapter: FakeBankClient → PaymentGateway
│   └── notifications.py   EmailNotifier, AuditLog observers
├── api/               FastAPI (schemas, routes, app + error mapping)
└── bootstrap.py       composition root, wires everything together
tests/
docs/
├── adr/0001-architectural-style.md
└── refactors/001-split-reservation-service.md
```

## Sprint A checklist

| # | Module | Requirement | Where it lives |
|---|---|---|---|
| 1 | M1 | Layered package structure, plus `tests/` and `docs/` | `src/pitch_booking/{domain,application,infrastructure,api}/`, `tests/`, `docs/` |
| 2 | M2 | SOLID refactor (SRP, plus DIP and OCP) with before and after | `docs/refactors/001-split-reservation-service.md`. Naive version is in the git history; refactored version is `src/pitch_booking/application/reservation_service.py` |
| 3a | M3 | **Factory** (creational) | `src/pitch_booking/domain/factories.py` (`SlotFactory`, `ReservationFactory`) |
| 3b | M3 | **Adapter** (structural) | `src/pitch_booking/infrastructure/payment_adapter.py` adapts `fakebank_sdk.py` to the `PaymentGateway` port |
| 3c | M3 | **Repository** behind an interface | `src/pitch_booking/application/ports.py` (interfaces), `src/pitch_booking/infrastructure/in_memory_repositories.py` (implementations) |
| 4a | M4 | **Strategy**: pricing | `src/pitch_booking/domain/pricing.py` |
| 4b | M4 | **State**: reservation lifecycle | `src/pitch_booking/domain/reservation.py` |
| 4c | M4 | **Observer**: notifications | `src/pitch_booking/application/event_publisher.py`, `src/pitch_booking/infrastructure/notifications.py` |
| 5 | M5 | Architectural style ADR (hexagonal monolith; services deferred to M6–M7) | `docs/adr/0001-architectural-style.md` |
| — | — | Tests: pricing, state transitions, slot availability | `tests/test_pricing.py`, `tests/test_reservation_state.py`, `tests/test_slot_availability.py` |

## Design patterns at a glance

- **Factory:** `ReservationFactory` is the only place a `Reservation` is built. It validates
  the e-mail, whole-hour start, 1–3 hours and opening hours, and prices the booking.
  `SlotFactory` generates a day's hourly slots with prices.
- **Adapter:** `FakeBankClient` has its own vendor-style API
  (`make_transaction(card_no, amount_kurus, …) -> dict`). `FakeBankPaymentAdapter`
  converts it to our `PaymentGateway.charge(amount, card, reference) -> txn_id` and turns a
  decline into `PaymentDeclinedError`.
- **Repository:** use cases depend on `PitchRepository` / `ReservationRepository`. The
  in-memory implementations can later be replaced by a SQL implementation.
- **Strategy:** `NormalPricing`, `PeakHourPricing` and `WeekendPricing` implement
  `PricingStrategy`. `PriceCalculator` picks the first strategy that applies to each hour,
  in priority order (weekend > peak > normal).
- **State:** `PendingState`, `ConfirmedState` and `CancelledState` decide which transitions
  are allowed. An invalid transition raises `InvalidStateTransitionError` (HTTP 409). A
  cancelled reservation no longer blocks its slot.
- **Observer:** `ReservationService` publishes `ReservationCreated`, `ReservationConfirmed`
  and `ReservationCancelled` events. `EmailNotifier` and `AuditLog` subscribe to them in
  `bootstrap.py`.

## Code conventions

The Python source contains no comments or docstrings by design. Explanations live in this
README and in `docs/`.
