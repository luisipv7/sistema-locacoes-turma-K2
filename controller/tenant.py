from sqlmodel import Session

from models.tenant import Tenant
from schemas.tenant_schema import TenantCreate, TenantUpdate
from services.tenant import delete_tenant_service, create_tenant_service, update_tenant_service, get_all_tenant_service

async def delete_tenant(session, tenant_id: int):
    return await delete_tenant_service(session, tenant_id)

async def update_tenant(session: Session, id: int, tenant: TenantUpdate):
    return await update_tenant_service(session, id, tenant)

async def create_tenant(session: Session, tenant: TenantCreate) -> Tenant:
    return await create_tenant_service(session, tenant)

async def get_all_tenant(session: Session, skip: int = 0, limit: int | None = None, id: int| None= None):
    return await get_all_tenant_service(session, skip, limit, id)