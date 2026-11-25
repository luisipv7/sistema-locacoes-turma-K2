from sqlmodel import Session

from models.tenant import Tenant
from schemas.tenant_schema import TenantCreate, TenantUpdate
from services.tenant import (
    create_tenant_service,
    delete_tenant_service,
    get_all_tenant_service,
    get_tenant_service,
    update_tenant_service,
)


async def create_tenant(session: Session, tenant: TenantCreate) -> Tenant:
    return await create_tenant_service(session, tenant)


async def get_all_tenant(session: Session, skip: int = 0, limit: int | None = None) -> list[Tenant]:
    return await get_all_tenant_service(session, skip, limit)


async def get_tenant(session: Session, tenant_id: int) -> Tenant:
    return await get_tenant_service(session, tenant_id)


async def update_tenant(session: Session, tenant_id: int, tenant: TenantUpdate) -> Tenant:
    return await update_tenant_service(session, tenant_id, tenant)


async def delete_tenant(session: Session, tenant_id: int) -> Tenant:
    return await delete_tenant_service(session, tenant_id)
