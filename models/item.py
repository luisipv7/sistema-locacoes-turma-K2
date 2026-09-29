
from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Column, Numeric, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from models.base import TimestampMixin
from models.enums import ItemStatus

# if TYPE_CHECKING:
#     from app.models.booking import Booking
#     from app.models.category import Category
#     from app.models.tenant import Tenant
#     from app.models.user import User


class Item(TimestampMixin, SQLModel, table=True):
    __tablename__ = "items"

    # __table_args__ = (
    #     UniqueConstraint("tenant_id", "slug", name="uq_items_tenant_slug"),
    # )

    id: int | None = Field(default=None, primary_key=True)

    tenant_id: int = Field(default=None, index=True)
    category_id: int = Field(default=None, index=True)
    owner_id: int = Field(default=None, index=True)

    name: str = Field(max_length=150)
    slug: str = Field(index=True, max_length=150)
    description: str | None = Field(default=None, max_length=1000)

    daily_price: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(Numeric(10, 2), nullable=False),
    )
    hourly_price: Decimal | None = Field(
        default=None,
        sa_column=Column(Numeric(10, 2), nullable=True),
    )

    image_url: str | None = Field(default=None, max_length=500)

    status: ItemStatus = Field(default=ItemStatus.AVAILABLE, index=True)
    is_active: bool = Field(default=True)

    # tenant: "Tenant" = Relationship(back_populates="items")
    # category: "Category" = Relationship(back_populates="items")
    # owner: "User" = Relationship(back_populates="items")
    # bookings: list["Booking"] = Relationship(back_populates="item")