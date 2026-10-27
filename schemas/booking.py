# schemas/booking_schema.py

from datetime import datetime
from decimal import Decimal

from sqlmodel import SQLModel

from models.enums import BookingStatus


class BookingCreate(SQLModel):
    tenant_id: int
    item_id: int
    user_id: int
    start_at: datetime
    end_at: datetime
    notes: str | None = None


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
    status: BookingStatus | None = None
    total_amount: Decimal | None = None
    notes: str | None = None