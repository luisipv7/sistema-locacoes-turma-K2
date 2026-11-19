from fastapi import APIRouter, Depends
from sqlmodel import Session

from controller.booking import BookingController
from controller.permissions import StaffUser
from database import get_session
from models.booking import Booking
from schemas.booking import BookingCreate, BookingRead

router = APIRouter(prefix="/bookings", tags=["bookings"])

# criar: admin e locador


@router.post("/", response_model=BookingRead, status_code=201)
async def create_booking(
    booking: BookingCreate,
    current_user: StaffUser,
    session: Session = Depends(get_session),
) -> Booking:
    return await BookingController.create_booking(session, current_user, booking)