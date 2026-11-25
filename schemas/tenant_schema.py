# /schemas/tenant_schema.py

from sqlmodel import Field, SQLModel

from models.enums import TenantStatus


class TenantCreate(SQLModel):
    name: str = Field(max_length=100)
    slug: str = Field(max_length=100)
    domain: str | None = None
    logo_url: str | None = None
    currency: str = "BRL"
    timezone: str = "America/Sao_Paulo"
    language: str = "pt-BR"
    min_rental_hours: int = Field(default=2, ge=1)
    max_rental_days: int = Field(default=30, ge=1)
    advance_booking_days: int = Field(default=90, ge=0)


class TenantRead(SQLModel):
    id: int
    name: str
    slug: str
    domain: str | None
    logo_url: str | None
    currency: str
    timezone: str
    language: str
    min_rental_hours: int
    max_rental_days: int
    advance_booking_days: int
    status: TenantStatus


class TenantUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=100)
    slug: str | None = Field(default=None, max_length=100)
    domain: str | None = None
    logo_url: str | None = None
    currency: str | None = None
    timezone: str | None = None
    language: str | None = None
    min_rental_hours: int | None = Field(default=None, ge=1)
    max_rental_days: int | None = Field(default=None, ge=1)
    advance_booking_days: int | None = Field(default=None, ge=0)
    status: TenantStatus | None = None
