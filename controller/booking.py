from datetime import datetime

from fastapi import HTTPException, status
from sqlmodel import Session

from controller.permissions import check_tenant_access, resolve_tenant_id
from models.booking import Booking
from models.enums import BookingStatus, UserRole
from models.user import User
from schemas.booking import AvailabilityRead, BookingCreate, BookingUpdate, MyRentalRead
from services.booking import (
    change_booking_status_service,
    check_availability_service,
    create_booking_service,
    get_booking_service,
    list_bookings_service,
    list_my_rentals_service,
    update_booking_service,
)
from services.item import ItemService


async def create_booking(session: Session, current_user: User, booking: BookingCreate) -> Booking:
    check_tenant_access(current_user, booking.tenant_id)
    # o cliente so pode alugar para ele mesmo
    if current_user.role == UserRole.CLIENTE and booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="O cliente so pode criar locacao para ele mesmo",
        )
    return await create_booking_service(session, booking)


async def list_bookings(
    session: Session,
    current_user: User,
    tenant_id: int | None = None,
    item_id: int | None = None,
    user_id: int | None = None,
    booking_status: BookingStatus | None = None,
) -> list[Booking]:
    tenant_id = resolve_tenant_id(current_user, tenant_id)
    return await list_bookings_service(session, tenant_id, item_id, user_id, booking_status)


async def list_my_rentals(session: Session, current_user: User) -> list[MyRentalRead]:
    # o user_id vem do TOKEN, nunca da URL: o cliente nao tem como ver as de outra pessoa
    bookings = await list_my_rentals_service(session, current_user.id)
    return [
        MyRentalRead(
            booking_id=booking.id,
            item_id=booking.item_id,
            item_name=booking.item.name,  # relacionamento Booking -> Item
            item_image_url=booking.item.image_url,
            data_retirada=booking.start_at,
            data_devolucao=booking.end_at,
            status=booking.status,
            total_amount=booking.total_amount,
        )
        for booking in bookings
    ]


async def check_availability(
    session: Session, current_user: User, item_id: int, start_at: datetime, end_at: datetime
) -> AvailabilityRead:
    item = await ItemService.get_by_id(session, item_id)
    check_tenant_access(current_user, item.tenant_id)
    available = await check_availability_service(session, item_id, start_at, end_at)
    return AvailabilityRead(item_id=item_id, start_at=start_at, end_at=end_at, available=available)


async def get_booking(session: Session, current_user: User, booking_id: int) -> Booking:
    booking = await get_booking_service(session, booking_id)
    check_tenant_access(current_user, booking.tenant_id)
    return booking


async def update_booking(
    session: Session, current_user: User, booking_id: int, booking: BookingUpdate
) -> Booking:
    await get_booking(session, current_user, booking_id)
    return await update_booking_service(session, booking_id, booking)


async def confirm_booking(session: Session, current_user: User, booking_id: int) -> Booking:
    await get_booking(session, current_user, booking_id)
    return await change_booking_status_service(session, booking_id, BookingStatus.CONFIRMED)


async def cancel_booking(session: Session, current_user: User, booking_id: int) -> Booking:
    await get_booking(session, current_user, booking_id)
    return await change_booking_status_service(session, booking_id, BookingStatus.CANCELLED)


async def complete_booking(session: Session, current_user: User, booking_id: int) -> Booking:
    await get_booking(session, current_user, booking_id)
    return await change_booking_status_service(session, booking_id, BookingStatus.COMPLETED)
