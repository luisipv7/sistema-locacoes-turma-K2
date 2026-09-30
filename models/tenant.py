# app/models/tenant.py

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from models.base import TimestampMixin
from models.enums import TenantStatus

# if TYPE_CHECKING:
#     from app.models.booking import Booking
#     from app.models.category import Category
#     from app.models.item import Item
#     from app.models.user import User


class Tenant(TimestampMixin, SQLModel, table=True):
    __tablename__ = "tenants"

    id: int | None = Field(default=None, primary_key=True)

    name: str = Field(max_length=100)
    slug: str = Field(index=True, unique=True, max_length=100)
    domain: str | None = Field(default=None, index=True, max_length=255)
    logo_url: str | None = Field(default=None, max_length=500)

    currency: str = Field(default="BRL", max_length=3)
    timezone: str = Field(default="America/Sao_Paulo", max_length=60)
    language: str = Field(default="pt-BR", max_length=10)

    min_rental_hours: int = Field(default=2)
    max_rental_days: int = Field(default=30)
    advance_booking_days: int = Field(default=90)

    status: TenantStatus = Field(default=TenantStatus.ACTIVE)

    # users: list["User"] = Relationship(back_populates="tenant")
    # categories: list["Category"] = Relationship(back_populates="tenant")
    # items: list["Item"] = Relationship(back_populates="tenant")
    # bookings: list["Booking"] = Relationship(back_populates="tenant")