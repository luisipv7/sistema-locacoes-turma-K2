# schemas/item_schema.py

from decimal import Decimal

from sqlmodel import SQLModel

from app.models.enums import ItemStatus


class ItemCreate(SQLModel):
    tenant_id: int
    category_id: int | None = None
    owner_id: int | None = None
    name: str
    slug: str
    description: str | None = None
    daily_price: Decimal = Decimal("0.00")
    hourly_price: Decimal | None = None
    image_url: str | None = None
    status: ItemStatus = ItemStatus.AVAILABLE


class ItemRead(SQLModel):
    id: int
    tenant_id: int
    category_id: int | None
    owner_id: int | None 
    name: str
    slug: str
    description: str | None
    daily_price: Decimal
    hourly_price: Decimal | None
    image_url: str | None
    status: ItemStatus
    is_active: bool


class ItemUpdate(SQLModel):
    category_id: int | None = None
    owner_id: int | None = None
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    daily_price: Decimal | None = None
    hourly_price: Decimal | None = None
    image_url: str | None = None
    status: ItemStatus | None = None
    is_active: bool | None = None