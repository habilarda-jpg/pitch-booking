# Pitch Booking – Halı Saha Rezervasyon Sistemi

Course project for **Software Design and Architecture**, Sprint A (Modules 1–5).

## Design brief

**Problem.** Booking a halı saha (5–7-a-side football pitch) is usually done by phone or
WhatsApp. Players can't see which hours are free or what a given hour costs, owners keep
schedules on paper, and the same hour is easily promised to two teams. We want a simple
online system where players see real availability and prices, and owners keep control of
their pitches and prices.

**Main use cases**

| Actor | Use case |
|---|---|
| Customer | Browse pitches |
| Customer | See the free hourly slots of a pitch for a date, with the price of each slot |
| Customer | Reserve one or more consecutive hours (reservation starts as *Pending*) |
| Customer | Pay for a reservation with the mock payment provider (*Pending → Confirmed*) |
| Customer | Cancel a reservation (*Pending/Confirmed → Cancelled*, the slot is freed) |
| Pitch owner | Register a pitch and change its hourly price (only the owner may) |

**Key quality attributes**

| Attribute | How it is addressed |
|---|---|
| **Consistency: no double booking** | Every reservation is checked against active reservations for overlap on the server (`Reservation.overlaps`, `ReservationService.create_reservation`). Cancelled reservations release their slot. The UI never decides availability. |
| **Correct lifecycle** | The State pattern only allows valid transitions. A cancelled reservation can never be paid, and the card is not charged unless the transition is allowed. |
| **Modifiability** | Hexagonal layers and ports. New tariffs (Strategy), payment providers (Adapter), storage (Repository) or notification channels (Observer) are added as new classes. |
| **Testability** | The domain and use cases have no framework or I/O dependencies, so pytest runs fast without a server or database. |
| **Usability and accessibility** | Clear slot grid, prices on every slot, status badges, friendly error messages taken from the API, confirmation before cancelling, keyboard focus styles, labelled inputs, WCAG AA contrast. |

Pricing: weekday 09–18 = base price · weekday 18–24 = base × 1.3 (peak) · weekend = base × 1.5.
Opening hours are 09:00–24:00, and a reservation is 1–3 whole hours long.

Tech: Python 3.12, [uv](https://docs.astral.sh/uv/), FastAPI, pytest · Vite, React 19,
TypeScript, plain CSS. There is no real database yet; data lives in memory and is lost
when the backend restarts.

## How to run

> **Windows note:** on this machine Application Control blocks the `uvicorn.exe` and
> `pytest.exe` launchers that uv puts in `.venv\Scripts`. Always start them as Python
> modules (`python -m …`), as shown below.

You need **uv** (Python 3.12 is installed automatically) and **Node.js 20.19+ or 22.12+**.

### Backend and frontend together (two terminals)

**Terminal 1: backend API** (from the project root):

```powershell
uv sync
uv run python -m uvicorn pitch_booking.api.app:app --reload
```

The API runs on <http://localhost:8000>, and the interactive docs are at
<http://localhost:8000/docs>. Two demo pitches are seeded on startup.

**Terminal 2: frontend** (from the project root):

```powershell
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>. The frontend calls the API at `http://localhost:8000` by
default. To use another address, copy `frontend/.env.example` to `frontend/.env.local`
and change `VITE_API_URL`. The backend allows CORS from `http://localhost:5173` only.

Production build of the frontend: `npm run build` (output goes to `frontend/dist/`).

Mock bank test cards: `4242 4242 4242 4242` is approved and `4000 0000 0000 0002` is
declined. Any 16-digit card ending in `0002` is declined.

### API endpoints

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

Errors return `{"detail": "..."}` with 400 (invalid input), 402 (payment declined),
403 (not the owner), 404 (not found) or 409 (slot taken / invalid state transition).
The frontend shows the `detail` text to the user.

## How to test

```powershell
uv run python -m pytest
```

| Test file | Covers |
|---|---|
| `tests/test_pricing.py` | Normal / peak / weekend strategies, multi-hour totals, adding a new strategy (OCP) |
| `tests/test_reservation_state.py` | All valid and invalid state transitions |
| `tests/test_slot_availability.py` | Daily slots, booked or cancelled slots, overlap, opening-hours validation |
| `tests/test_reservation_service.py` | Use cases, payment adapter, observers, owner-only price change |
| `tests/test_api.py` | End-to-end HTTP flow, error → status-code mapping, CORS for the Vite origin |

Frontend type-check and build: `cd frontend && npm run build`.

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
├── api/               FastAPI (schemas, routes, app + error mapping + CORS)
└── bootstrap.py       composition root, wires everything together
frontend/              separate React client (talks to the API over HTTP only)
├── index.html
└── src/
    ├── api/               all HTTP calls: client.ts, pitches.ts, reservations.ts, types.ts
    ├── pages/             PitchListPage, PitchDetailPage, MyReservationsPage
    ├── components/        NavBar, ReservationCard, StatusBadge, Feedback (alerts, loading)
    ├── styles/            theme.css (all color variables), app.css
    ├── router.ts          tiny hash router
    ├── storage.ts         remembers "my reservations" IDs in localStorage
    └── format.ts          price, date and time formatting
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
| 5 | M5 | Architectural style ADR (hexagonal monolith; MVC compared; services deferred to M6–M7) | `docs/adr/0001-architectural-style.md` |
| 6 | M5 | **Frontend as a separate presentation client** (React view over the REST API) | `frontend/` (all API calls in `frontend/src/api/`); CORS in `src/pitch_booking/api/app.py`; rationale in the ADR section *Presentation: a separate frontend client* |
| 7 | — | Frontend screens: pitch list, slots and booking, my reservations (pay/cancel) | `frontend/src/pages/PitchListPage.tsx`, `PitchDetailPage.tsx`, `MyReservationsPage.tsx` |
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

## Frontend design notes

- **Palette:** white and very light green-gray surfaces, one pitch-green primary
  (`#15803d`) for buttons, links and active states, a dark green (`#14532d`) for headings,
  and neutral grays for secondary text. Every color is a CSS variable in
  `frontend/src/styles/theme.css`; `app.css` uses only those variables.
- **Slots:** a grid of large buttons. Available = green outline, selected = solid green,
  booked or past = grayed out and disabled. Each slot shows its price.
- **Status badges:** Pending = amber, Confirmed = green, Cancelled = gray.
- **Feedback:** loading spinners, success and error alerts that show the API's `detail`
  text, and an inline "Cancel this reservation?" confirmation.
- **Accessibility:** labelled inputs, visible focus rings, a skip link, `aria-pressed` on
  slots, and text/background contrast of at least 4.5:1.
- **Responsive:** the layout goes from two columns (slots and booking panel) on desktop
  to one column on mobile, with a simple sticky top navigation.

## Code conventions

The source code (Python, TypeScript and CSS) contains no comments or docstrings by
design. Explanations live in this README and in `docs/`.
