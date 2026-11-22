from controller.permissions import StaffUser, check_tenant_access
from models.booking import Booking
from schemas.booking import BookingCreate
from services.booking import BookingService

from sqlmodel import Session


class BookingController:

    async def create_booking(
        session: Session, current_user: StaffUser, booking: BookingCreate
    ) -> Booking:
        check_tenant_access(current_user, booking.tenant_id)
        return await BookingService.create_booking(session, booking)