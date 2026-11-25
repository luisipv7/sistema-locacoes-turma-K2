# schemas/item_schema.py

from decimal import Decimal

from sqlmodel import Field, SQLModel

from models.enums import ItemStatus


class ItemCreate(SQLModel):
    tenant_id: int
    category_id: int | None = None
    owner_id: int | None = None
    name: str = Field(max_length=150)
    slug: str = Field(max_length=150)
    description: str | None = Field(default=None, max_length=1000)
    daily_price: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    hourly_price: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    image_url: str | None = None


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
    name: str | None = Field(default=None, max_length=150)
    slug: str | None = Field(default=None, max_length=150)
    description: str | None = Field(default=None, max_length=1000)
    daily_price: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    hourly_price: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    image_url: str | None = None
    status: ItemStatus | None = None
    is_active: bool | None = None
