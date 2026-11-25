from datetime import datetime
from decimal import Decimal

from sqlmodel import Field, SQLModel

from models.enums import BookingStatus


class BookingCreate(SQLModel):
    tenant_id: int
    item_id: int
    user_id: int          # o cliente que esta alugando
    start_at: datetime    # retirada
    end_at: datetime      # devolucao
    notes: str | None = Field(default=None, max_length=500)


class BookingRead(SQLModel):
    id: int
    tenant_id: int
    item_id: int
    user_id: int
    start_at: datetime
    end_at: datetime
    status: BookingStatus
    total_amount: Decimal | None
    notes: str | None


class BookingUpdate(SQLModel):
    start_at: datetime | None = None
    end_at: datetime | None = None
    notes: str | None = Field(default=None, max_length=500)


class AvailabilityRead(SQLModel):
    item_id: int
    start_at: datetime
    end_at: datetime
    available: bool