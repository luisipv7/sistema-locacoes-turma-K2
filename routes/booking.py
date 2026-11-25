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
    list_my_rentals,
    update_booking,
)
from controller.permissions import ClienteUser, CurrentUser, StaffUser
from database import get_session
from models.enums import BookingStatus
from schemas.booking import (
    AvailabilityRead,
    BookingCreate,
    BookingRead,
    BookingUpdate,
    MyRentalRead,
)

router = APIRouter(prefix="/bookings", tags=["bookings"])

# criar e consultar disponibilidade: qualquer usuario logado (o cliente so para ele mesmo)
# listar e gerenciar: admin e locador
# /me: so o cliente, para ver as locacoes dele


@router.post("/", response_model=BookingRead, status_code=status.HTTP_201_CREATED)
async def create_booking_route(
    booking: BookingCreate, current_user: CurrentUser, session: Session = Depends(get_session)
):
    return await create_booking(session, current_user, booking)


@router.get("/", response_model=list[BookingRead])
async def list_bookings_route(
    current_user: StaffUser,
    tenant_id: int | None = None,
    item_id: int | None = None,
    user_id: int | None = None,
    booking_status: BookingStatus | None = None,
    session: Session = Depends(get_session),
):
    return await list_bookings(session, current_user, tenant_id, item_id, user_id, booking_status)


# "/availability" e "/me" precisam vir ANTES de "/{booking_id}",
# senao o FastAPI tenta ler "availability" / "me" como id
@router.get("/availability", response_model=AvailabilityRead)
async def check_availability_route(
    item_id: int,
    start_at: datetime,
    end_at: datetime,
    current_user: CurrentUser,
    session: Session = Depends(get_session),
):
    return await check_availability(session, current_user, item_id, start_at, end_at)


@router.get("/me", response_model=list[MyRentalRead])
async def list_my_rentals_route(current_user: ClienteUser, session: Session = Depends(get_session)):
    return await list_my_rentals(session, current_user)


@router.get("/{booking_id}", response_model=BookingRead)
async def get_booking_route(
    booking_id: int, current_user: StaffUser, session: Session = Depends(get_session)
):
    return await get_booking(session, current_user, booking_id)


@router.patch("/{booking_id}", response_model=BookingRead)
async def update_booking_route(
    booking_id: int,
    booking: BookingUpdate,
    current_user: StaffUser,
    session: Session = Depends(get_session),
):
    return await update_booking(session, current_user, booking_id, booking)


@router.post("/{booking_id}/confirm", response_model=BookingRead)
async def confirm_booking_route(
    booking_id: int, current_user: StaffUser, session: Session = Depends(get_session)
):
    return await confirm_booking(session, current_user, booking_id)


@router.post("/{booking_id}/cancel", response_model=BookingRead)
async def cancel_booking_route(
    booking_id: int, current_user: StaffUser, session: Session = Depends(get_session)
):
    return await cancel_booking(session, current_user, booking_id)


@router.post("/{booking_id}/complete", response_model=BookingRead)
async def complete_booking_route(
    booking_id: int, current_user: StaffUser, session: Session = Depends(get_session)
):
    return await complete_booking(session, current_user, booking_id)
