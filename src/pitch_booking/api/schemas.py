from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from pitch_booking.domain.pitch import Pitch
from pitch_booking.domain.reservation import Reservation
from pitch_booking.domain.slot import Slot


class PitchCreate(BaseModel):
    name: str = Field(min_length=1)
    owner_id: int
    hourly_price: Decimal = Field(gt=0)


class PriceUpdate(BaseModel):
    owner_id: int
    hourly_price: Decimal = Field(gt=0)


class PitchOut(BaseModel):
    id: int
    name: str
    owner_id: int
    hourly_price: Decimal

    @classmethod
    def of(cls, pitch: Pitch) -> "PitchOut":
        return cls(
            id=pitch.id, name=pitch.name, owner_id=pitch.owner_id, hourly_price=pitch.hourly_price
        )


class SlotOut(BaseModel):
    start: datetime
    end: datetime
    price: Decimal
    available: bool

    @classmethod
    def of(cls, slot: Slot) -> "SlotOut":
        return cls(start=slot.start, end=slot.end, price=slot.price, available=slot.available)


class ReservationCreate(BaseModel):
    pitch_id: int
    customer_email: str
    start: datetime
    hours: int = 1


class PaymentRequest(BaseModel):
    card_number: str


class ReservationOut(BaseModel):
    id: int
    pitch_id: int
    customer_email: str
    start: datetime
    end: datetime
    hours: int
    price: Decimal
    status: str
    payment_reference: str | None

    @classmethod
    def of(cls, r: Reservation) -> "ReservationOut":
        return cls(
            id=r.id,
            pitch_id=r.pitch_id,
            customer_email=r.customer_email,
            start=r.start,
            end=r.end,
            hours=r.hours,
            price=r.price,
            status=r.status.value,
            payment_reference=r.payment_reference,
        )
