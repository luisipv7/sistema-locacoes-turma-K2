import math
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlmodel import Session, col, select

from models.booking import Booking
from models.enums import BookingStatus, ItemStatus
from models.item import Item
from models.tenant import Tenant
from models.user import User
from schemas.booking import BookingCreate


def _to_utc(value: datetime) -> datetime:
    """Se a data veio sem fuso, assume UTC; senão converte para UTC."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _calculate_total(item: Item, start_at: datetime, end_at: datetime) -> Decimal:
    """Menos de 24h usa o preço por hora (se existir); senão cobra por diária."""
    hours = math.ceil((end_at - start_at).total_seconds() / 3600)
    if item.hourly_price is not None and hours < 24:
        total = item.hourly_price * hours
    else:
        total = item.daily_price * math.ceil(hours / 24)
    return Decimal(total).quantize(Decimal("0.01"))


class BookingService:

    async def create_booking(session: Session, data: BookingCreate) -> Booking:

        # 1. tenant, usuário e item precisam existir e ser do mesmo tenant
        if not session.get(Tenant, data.tenant_id):
            raise HTTPException(status_code=404, detail="Tenant nao encontrado")

        user = session.get(User, data.user_id)
        if not user or user.tenant_id != data.tenant_id:
            raise HTTPException(status_code=404, detail="Usuario nao encontrado")

        # with_for_update() trava o item para duas reservas não passarem juntas
        item = session.exec(
            select(Item).where(Item.id == data.item_id).with_for_update()
        ).first()
        if not item or item.tenant_id != data.tenant_id:
            raise HTTPException(status_code=404, detail="Item nao encontrado")

        if not item.is_active or item.status != ItemStatus.AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Item indisponivel para locacao",
            )

        # 2. datas
        start_at = _to_utc(data.start_at)
        end_at = _to_utc(data.end_at)
        if end_at <= start_at:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="O termino deve ser depois do inicio",
            )
        if start_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="O inicio nao pode estar no passado",
            )

        # 3. o item não pode ter outra locação pendente/confirmada no período
        conflict = session.exec(
            select(Booking).where(
                Booking.item_id == item.id,
                col(Booking.status).in_(
                    [BookingStatus.PENDING, BookingStatus.CONFIRMED]
                ),
                Booking.start_at < end_at,
                Booking.end_at > start_at,
            )
        ).first()
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Item ja reservado nesse periodo",
            )

        # 4. o valor total é calculado pelo servidor
        new_booking = Booking(
            tenant_id=data.tenant_id,
            item_id=item.id,
            user_id=user.id,
            start_at=start_at,
            end_at=end_at,
            status=BookingStatus.PENDING,
            total_amount=_calculate_total(item, start_at, end_at),
            notes=data.notes,
        )
        session.add(new_booking)
        session.commit()
        session.refresh(new_booking)
        return new_booking