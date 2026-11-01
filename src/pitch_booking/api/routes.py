from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Request, status

from pitch_booking.api.schemas import (
    PaymentRequest,
    PitchCreate,
    PitchOut,
    PriceUpdate,
    ReservationCreate,
    ReservationOut,
    SlotOut,
)
from pitch_booking.bootstrap import Container


def get_container(request: Request) -> Container:
    return request.app.state.container


ContainerDep = Annotated[Container, Depends(get_container)]

router = APIRouter()


@router.get("/pitches", response_model=list[PitchOut])
def list_pitches(c: ContainerDep) -> list[PitchOut]:
    return [PitchOut.of(p) for p in c.pitch_service.list_pitches()]


@router.post("/pitches", response_model=PitchOut, status_code=status.HTTP_201_CREATED)
def create_pitch(body: PitchCreate, c: ContainerDep) -> PitchOut:
    return PitchOut.of(c.pitch_service.register_pitch(body.name, body.owner_id, body.hourly_price))


@router.patch("/pitches/{pitch_id}/price", response_model=PitchOut)
def change_price(pitch_id: int, body: PriceUpdate, c: ContainerDep) -> PitchOut:
    return PitchOut.of(c.pitch_service.change_price(pitch_id, body.owner_id, body.hourly_price))


@router.get("/pitches/{pitch_id}/slots", response_model=list[SlotOut])
def list_slots(pitch_id: int, day: date, c: ContainerDep) -> list[SlotOut]:
    return [SlotOut.of(s) for s in c.availability_service.slots_for_day(pitch_id, day)]


@router.post("/reservations", response_model=ReservationOut, status_code=status.HTTP_201_CREATED)
def create_reservation(body: ReservationCreate, c: ContainerDep) -> ReservationOut:
    reservation = c.reservation_service.create_reservation(
        body.pitch_id, body.customer_email, body.start, body.hours
    )
    return ReservationOut.of(reservation)


@router.get("/reservations/{reservation_id}", response_model=ReservationOut)
def get_reservation(reservation_id: int, c: ContainerDep) -> ReservationOut:
    return ReservationOut.of(c.reservation_service.get_reservation(reservation_id))


@router.post("/reservations/{reservation_id}/pay", response_model=ReservationOut)
def pay_reservation(reservation_id: int, body: PaymentRequest, c: ContainerDep) -> ReservationOut:
    return ReservationOut.of(c.reservation_service.pay(reservation_id, body.card_number))


@router.post("/reservations/{reservation_id}/cancel", response_model=ReservationOut)
def cancel_reservation(reservation_id: int, c: ContainerDep) -> ReservationOut:
    return ReservationOut.of(c.reservation_service.cancel(reservation_id))
