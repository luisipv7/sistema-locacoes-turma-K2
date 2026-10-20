# /schemas/tenant_schema.py

from sqlmodel import SQLModel

from app.models.enums import TenantStatus


class TenantCreate(SQLModel):
    name: str
    slug: str
    domain: str | None = None
    logo_url: str | None = None
    currency: str = "BRL"
    timezone: str = "America/Sao_Paulo"
    language: str = "pt-BR"
    min_rental_hours: int = 2
    max_rental_days: int = 30
    advance_booking_days: int = 90


class TenantRead(SQLModel):
    id: int
    name: str
    slug: str
    domain: str | None
    logo_url: str | None
    currency: str
    timezone: str
    language: str
    status: TenantStatus


class TenantUpdate(SQLModel):
    name: str | None = None
    slug: str | None = None
    domain: str | None = None
    logo_url: str | None = None
    currency: str | None = None
    timezone: str | None = None
    language: str | None = None
    min_rental_hours: int | None = None
    max_rental_days: int | None = None
    advance_booking_days: int | None = None
    status: TenantStatus | None = None