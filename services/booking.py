import math
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlmodel import Session, col, select

from models.booking import Booking
from models.enums import BookingStatus, ItemStatus, TenantStatus
from models.item import Item
from models.tenant import Tenant
from models.user import User
from schemas.booking import BookingCreate, BookingUpdate

ACTIVE_STATUSES = [BookingStatus.PENDING, BookingStatus.CONFIRMED]

ALLOWED_TRANSITIONS = {
    BookingStatus.PENDING: {BookingStatus.CONFIRMED, BookingStatus.CANCELLED},
    BookingStatus.CONFIRMED: {BookingStatus.COMPLETED, BookingStatus.CANCELLED},
    BookingStatus.CANCELLED: set(),
    BookingStatus.COMPLETED: set(),
}


def _error(code: int, message: str) -> HTTPException:
    return HTTPException(status_code=code, detail=message)


def _to_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _get_active_tenant(session: Session, tenant_id: int) -> Tenant:
    tenant = session.get(Tenant, tenant_id)
    if not tenant or tenant.status != TenantStatus.ACTIVE:
        raise _error(status.HTTP_404_NOT_FOUND, "Tenant nao encontrado")
    return tenant


def _get_bookable_item(session: Session, tenant_id: int, item_id: int) -> Item:
    statement = select(Item).where(Item.id == item_id).with_for_update()
    item = session.exec(statement).first()
    if not item or item.tenant_id != tenant_id:
        raise _error(status.HTTP_404_NOT_FOUND, "Item nao encontrado")
    if not item.is_active or item.status != ItemStatus.AVAILABLE:
        raise _error(status.HTTP_422_UNPROCESSABLE_ENTITY, "Item indisponivel para locacao")
    return item


def _get_active_user(session: Session, tenant_id: int, user_id: int) -> User:
    user = session.get(User, user_id)
    if not user or user.tenant_id != tenant_id:
        raise _error(status.HTTP_404_NOT_FOUND, "Usuario nao encontrado")
    if not user.is_active:
        raise _error(status.HTTP_422_UNPROCESSABLE_ENTITY, "Usuario inativo")
    return user


def _validate_period(tenant: Tenant, start_at: datetime, end_at: datetime) -> None:
    now = _now()
    if end_at <= start_at:
        raise _error(status.HTTP_422_UNPROCESSABLE_ENTITY, "A data final deve ser depois da data inicial")
    if start_at < now:
        raise _error(status.HTTP_422_UNPROCESSABLE_ENTITY, "Nao e possivel reservar no passado")
    if start_at > now + timedelta(days=tenant.advance_booking_days):
        raise _error(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            f"So e possivel reservar com ate {tenant.advance_booking_days} dias de antecedencia",
        )

    duration = end_at - start_at
    if duration < timedelta(hours=tenant.min_rental_hours):
        raise _error(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            f"A locacao minima e de {tenant.min_rental_hours} horas",
        )
    if duration > timedelta(days=tenant.max_rental_days):
        raise _error(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            f"A locacao maxima e de {tenant.max_rental_days} dias",
        )


def _has_overlap(
    session: Session,
    item_id: int,
    start_at: datetime,
    end_at: datetime,
    ignore_id: int | None = None,
) -> bool:
    statement = select(Booking).where(
        Booking.item_id == item_id,
        col(Booking.status).in_(ACTIVE_STATUSES),
        Booking.start_at < end_at,
        Booking.end_at > start_at,
    )
    if ignore_id is not None:
        statement = statement.where(Booking.id != ignore_id)
    return session.exec(statement).first() is not None


def calculate_total(item: Item, start_at: datetime, end_at: datetime) -> Decimal:
    hours = math.ceil((end_at - start_at).total_seconds() / 3600)
    if item.hourly_price is not None and hours < 24:
        total = item.hourly_price * hours
    else:
        days = math.ceil(hours / 24)
        total = item.daily_price * days
    return Decimal(total).quantize(Decimal("0.01"))


async def get_booking_service(session: Session, booking_id: int) -> Booking:
    booking = session.get(Booking, booking_id)
    if not booking:
        raise _error(status.HTTP_404_NOT_FOUND, "Locacao nao encontrada")
    return booking


async def list_bookings_service(
    session: Session,
    tenant_id: int,
    item_id: int | None = None,
    user_id: int | None = None,
    booking_status: BookingStatus | None = None,
) -> list[Booking]:
    statement = select(Booking).where(Booking.tenant_id == tenant_id)
    if item_id is not None:
        statement = statement.where(Booking.item_id == item_id)
    if user_id is not None:
        statement = statement.where(Booking.user_id == user_id)
    if booking_status is not None:
        statement = statement.where(Booking.status == booking_status)
    statement = statement.order_by(col(Booking.start_at))
    return list(session.exec(statement).all())


async def check_availability_service(
    session: Session, item_id: int, start_at: datetime, end_at: datetime
) -> bool:
    return not _has_overlap(session, item_id, _to_utc(start_at), _to_utc(end_at))


async def create_booking_service(session: Session, data: BookingCreate) -> Booking:
    tenant = _get_active_tenant(session, data.tenant_id)
    item = _get_bookable_item(session, data.tenant_id, data.item_id)
    _get_active_user(session, data.tenant_id, data.user_id)

    start_at = _to_utc(data.start_at)
    end_at = _to_utc(data.end_at)
    _validate_period(tenant, start_at, end_at)

    if _has_overlap(session, item.id, start_at, end_at):
        raise _error(status.HTTP_409_CONFLICT, "O item ja esta reservado nesse periodo")

    booking = Booking(
        tenant_id=data.tenant_id,
        item_id=item.id,
        user_id=data.user_id,
        start_at=start_at,
        end_at=end_at,
        notes=data.notes,
        total_amount=calculate_total(item, start_at, end_at),
    )
    session.add(booking)
    session.commit()
    session.refresh(booking)
    return booking


async def update_booking_service(session: Session, booking_id: int, data: BookingUpdate) -> Booking:
    booking = await get_booking_service(session, booking_id)
    if booking.status != BookingStatus.PENDING:
        raise _error(status.HTTP_422_UNPROCESSABLE_ENTITY, "So e possivel alterar locacoes pendentes")

    changes = data.model_dump(exclude_unset=True)

    if "start_at" in changes or "end_at" in changes:
        start_at = _to_utc(changes.get("start_at") or booking.start_at)
        end_at = _to_utc(changes.get("end_at") or booking.end_at)

        tenant = _get_active_tenant(session, booking.tenant_id)
        item = _get_bookable_item(session, booking.tenant_id, booking.item_id)
        _validate_period(tenant, start_at, end_at)

        if _has_overlap(session, item.id, start_at, end_at, ignore_id=booking.id):
            raise _error(status.HTTP_409_CONFLICT, "O item ja esta reservado nesse periodo")

        booking.start_at = start_at
        booking.end_at = end_at
        booking.total_amount = calculate_total(item, start_at, end_at)

    if "notes" in changes:
        booking.notes = changes["notes"]

    session.add(booking)
    session.commit()
    session.refresh(booking)
    return booking


async def change_booking_status_service(
    session: Session, booking_id: int, new_status: BookingStatus
) -> Booking:
    booking = await get_booking_service(session, booking_id)
    if new_status not in ALLOWED_TRANSITIONS[booking.status]:
        raise _error(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            f"Nao e possivel mudar de '{booking.status.value}' para '{new_status.value}'",
        )
    booking.status = new_status
    session.add(booking)
    session.commit()
    session.refresh(booking)
    return booking