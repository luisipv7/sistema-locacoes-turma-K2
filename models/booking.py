# app/models/booking.py

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Column, Numeric
from sqlmodel import Field, Relationship, SQLModel

from models.base import TimestampMixin
from models.enums import BookingStatus

# if TYPE_CHECKING:
#     from models.item import Item
#     from models.tenant import Tenant
#     from models.user import User


class Booking(TimestampMixin, SQLModel, table=True):
    __tablename__ = "bookings"

    # __table_args__ = (
    #     CheckConstraint("end_at > start_at", name="ck_bookings_end_after_start"),
    # )

    id: int | None = Field(default=None, primary_key=True)

    tenant_id: int = Field(default=None, index=True)
    item_id: int = Field(default=None, index=True)
    user_id: int = Field(default=None, index=True)

    start_at: datetime = Field(index=True)
    end_at: datetime = Field(index=True)

    status: BookingStatus = Field(default=BookingStatus.PENDING, index=True)

    total_amount: Decimal | None = Field(
        default=None,
        sa_column=Column(Numeric(10, 2), nullable=True),
    )

    notes: str | None = Field(default=None, max_length=500)

    # tenant: "Tenant" = Relationship(back_populates="bookings")
    # item: "Item" = Relationship(back_populates="bookings")
    # user: "User" = Relationship(back_populates="bookings")