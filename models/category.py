# models/category.py

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from models.base import TimestampMixin

# if TYPE_CHECKING:
#     from models.item import Item
#     from models.tenant import Tenant


class Category(TimestampMixin, SQLModel, table=True):
    __tablename__ = "categories"

    # __table_args__ = (
    #     UniqueConstraint("tenant_id", "slug", name="uq_categories_tenant_slug"),
    # )

    id: int | None = Field(default=None, primary_key=True)

    tenant_id: int = Field(default=None, index=True)

    name: str = Field(max_length=100)
    slug: str = Field(index=True, max_length=100) ## https://herospark.com/blog/o-que-e-slug/
    description: str | None = Field(default=None, max_length=500)

    parent_id: int | None = Field(default=None, index=True)

    # tenant: "Tenant" = Relationship(back_populates="categories")
    # items: list["Item"] = Relationship(back_populates="category")