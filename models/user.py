# app/models/user.py

#porque isso é necessário > https://www.reddit.com/r/learnpython/comments/1psteqc/why_does_from_future_import_annotations_matter_in/?tl=pt-br
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from models.base import TimestampMixin
from models.enums import UserRole

# if TYPE_CHECKING:
#     from models.booking import Booking
#     from models.item import Item
#     from models.tenant import Tenant


class User(TimestampMixin, SQLModel, table=True):
    __tablename__ = "users"

    # __table_args__ = (
    #     UniqueConstraint("tenant_id", "username", name="uq_users_tenant_username"),
    # )

    id: int | None = Field(default=None, primary_key=True)

    tenant_id: int = Field(default=None, index=True)
    # tenant_id: int = Field(foreign_key="tenants.id", index=True)

    username: str = Field(index=True, max_length=50, unique=True)
    hashed_password: str = Field(max_length=255)

    role: UserRole = Field(default=UserRole.CLIENTE)
    is_active: bool = Field(default=True)

    # tenant: "Tenant" = Relationship(back_populates="users")
    # items: list["Item"] = Relationship(back_populates="owner")
    # bookings: list["Booking"] = Relationship(back_populates="user")