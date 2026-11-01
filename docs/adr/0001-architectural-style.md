# ADR 0001 – Architectural style: Hexagonal (Ports & Adapters) modular monolith

- **Status:** Accepted
- **Date:** 2026-11-01
- **Module:** M5 – Architectural styles

## Context

We are building a football pitch (halı saha) reservation system. Customers browse pitches,
see free hourly slots, book, pay and cancel. Pitch owners manage pitches and prices.

Forces:

- **Small team, one semester.** The system must be simple to build, run and grade
  (`uv run …`, no extra infrastructure).
- **Infrastructure is not decided yet.** There is no real database (in-memory for now) and
  no real payment provider (mock "FakeBank"). Both will be replaced later.
- **Rich business rules.** Pricing tariffs, the reservation lifecycle and slot overlap need
  to be tested without HTTP or storage.
- **Later sprints (M6–M7)** will look at distributing the system, so module boundaries
  should already be clear.

## Decision

We use a **hexagonal (ports & adapters) architecture, deployed as a single monolith**.
The code is organised in four layers under `src/pitch_booking/`:

```
          api/  (driving adapter: FastAPI)
            │
            ▼
    application/  use cases + ports (interfaces)
            │                 ▲
            ▼                 │ implements
        domain/          infrastructure/  (driven adapters:
   entities, rules,       in-memory repos, FakeBank adapter,
   patterns, no I/O       e-mail / audit observers)
```

Dependency rule: **dependencies only point inwards.**

- `domain/` imports nothing from the other layers or from any framework.
- `application/` imports only `domain/`. It **defines** the ports `PitchRepository`,
  `ReservationRepository`, `PaymentGateway` and `ReservationObserver`.
- `infrastructure/` implements those ports.
- `api/` translates HTTP to use-case calls and maps `DomainError`s to status codes.
- `bootstrap.py` is the single **composition root** that wires concrete adapters to the
  ports.

## Alternatives considered

| Alternative | Why not (for now) |
|---|---|
| **Classic layered (N-tier)**: API → Service → DAO → DB | Simple, but the service layer usually depends directly on the DAO/DB, so the database becomes the centre of the design. Swapping persistence or payment is harder, and domain logic tends to leak into services. Hexagonal keeps the same simplicity but inverts those dependencies. |
| **Microservices**, e.g. Booking, Payment, Notification services | Brings network calls, distributed transactions (pay + confirm), deployment and monitoring overhead. That is not justified for one team, one database and no real load yet. |
| **Event-driven architecture with a message broker** | Notifications are already decoupled through an in-process Observer. A broker (RabbitMQ/Kafka) would add infrastructure with no current benefit. |
| **Transaction-script / "just FastAPI routes"** | Fastest to write, but this is essentially the naive version we refactored away from (see `docs/refactors/001-split-reservation-service.md`). Untestable business rules. |

## Consequences

**Positive**

- The domain and use cases are tested without FastAPI or a database: 40 fast tests.
- Swapping in-memory storage for PostgreSQL or FakeBank for a real provider (iyzico,
  Stripe…) means writing a new adapter and changing `bootstrap.py`. No use-case code
  changes.
- One process and one deploy, which is easy to run and debug.
- Ports already mark natural seams (payment, notification, availability) for a future split.

**Negative**

- More indirection (interfaces, factories, a composition root) than a tiny CRUD app
  strictly needs.
- Everything scales together. One bug can take the whole system down.
- In-memory adapters lose data on restart. This is acceptable for Sprint A only.

## Follow-up

**Splitting into separate services is explicitly deferred to Modules M6–M7.** Candidate
boundaries are the existing ports: a *Payment* service behind `PaymentGateway` and a
*Notification* service fed by `ReservationEvent`s, which would move from the in-process
`EventPublisher` to a message broker. That decision will get its own ADR.
