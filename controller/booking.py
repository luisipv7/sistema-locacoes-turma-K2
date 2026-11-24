from datetime import datetime

from sqlmodel import Session

from models.booking import Booking
from models.enums import BookingStatus
from schemas.booking import AvailabilityRead, BookingCreate, BookingUpdate
from services.booking import (
    change_booking_status_service,
    check_availability_service,
    create_booking_service,
    get_booking_service,
    list_bookings_service,
    update_booking_service,
)


async def create_booking(session: Session, booking: BookingCreate) -> Booking:
    return await create_booking_service(session, booking)


async def list_bookings(
    session: Session,
    tenant_id: int,
    item_id: int | None = None,
    user_id: int | None = None,
    booking_status: BookingStatus | None = None,
) -> list[Booking]:
    return await list_bookings_service(session, tenant_id, item_id, user_id, booking_status)


async def check_availability(
    session: Session, item_id: int, start_at: datetime, end_at: datetime
) -> AvailabilityRead:
    available = await check_availability_service(session, item_id, start_at, end_at)
    return AvailabilityRead(item_id=item_id, start_at=start_at, end_at=end_at, available=available)


async def get_booking(session: Session, booking_id: int) -> Booking:
    return await get_booking_service(session, booking_id)


async def update_booking(session: Session, booking_id: int, booking: BookingUpdate) -> Booking:
    return await update_booking_service(session, booking_id, booking)


async def confirm_booking(session: Session, booking_id: int) -> Booking:
    return await change_booking_status_service(session, booking_id, BookingStatus.CONFIRMED)


async def cancel_booking(session: Session, booking_id: int) -> Booking:
    return await change_booking_status_service(session, booking_id, BookingStatus.CANCELLED)


async def complete_booking(session: Session, booking_id: int) -> Booking:
    return await change_booking_status_service(session, booking_id, BookingStatus.COMPLETED)