from sqlmodel import Session

from models.tenant import Tenant
from schemas.tenant_schema import TenantCreate, TenantUpdate
from services.tenant import delete_tenant_service

async def delete_tenant(session, current_user, tenant_id: int):
    return await delete_tenant_service(session, tenant_id)

async def update_user(session: Session, id: int, tenant: TenantUpdate):
        return await update_user(session, id, tenant)

async def create(session: Session, tenant: TenantCreate) -> Tenant:
        return await create(session, tenant)

async def get_all(session: Session, skip: int = 0, limit: int | None = None) -> Item:
        return await get_all(session, skip, limit)