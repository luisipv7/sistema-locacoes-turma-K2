from datetime import datetime

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from controller.booking import (
    cancel_booking,
    check_availability,
    complete_booking,
    confirm_booking,
    create_booking,
    get_booking,
    list_bookings,
    update_booking,
)
from database import get_session
from models.enums import BookingStatus
from schemas.booking import AvailabilityRead, BookingCreate, BookingRead, BookingUpdate

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("/", response_model=BookingRead, status_code=status.HTTP_201_CREATED)
async def create_booking_route(booking: BookingCreate, session: Session = Depends(get_session)):
    return await create_booking(session, booking)


@router.get("/", response_model=list[BookingRead])
async def list_bookings_route(
    tenant_id: int,
    item_id: int | None = None,
    user_id: int | None = None,
    booking_status: BookingStatus | None = None,
    session: Session = Depends(get_session),
):
    return await list_bookings(session, tenant_id, item_id, user_id, booking_status)


@router.get("/availability", response_model=AvailabilityRead)
async def check_availability_route(
    item_id: int, start_at: datetime, end_at: datetime, session: Session = Depends(get_session)
):
    return await check_availability(session, item_id, start_at, end_at)


@router.get("/{booking_id}", response_model=BookingRead)
async def get_booking_route(booking_id: int, session: Session = Depends(get_session)):
    return await get_booking(session, booking_id)


@router.patch("/{booking_id}", response_model=BookingRead)
async def update_booking_route(
    booking_id: int, booking: BookingUpdate, session: Session = Depends(get_session)
):
    return await update_booking(session, booking_id, booking)


@router.post("/{booking_id}/confirm", response_model=BookingRead)
async def confirm_booking_route(booking_id: int, session: Session = Depends(get_session)):
    return await confirm_booking(session, booking_id)


@router.post("/{booking_id}/cancel", response_model=BookingRead)
async def cancel_booking_route(booking_id: int, session: Session = Depends(get_session)):
    return await cancel_booking(session, booking_id)


@router.post("/{booking_id}/complete", response_model=BookingRead)
async def complete_booking_route(booking_id: int, session: Session = Depends(get_session)):
    return await complete_booking(session, booking_id)