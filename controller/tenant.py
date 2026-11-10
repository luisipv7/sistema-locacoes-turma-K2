from sqlmodel import Session

from schemas.tenant_schema import TenantUpdate
from services.tenant import delete_tenant_service

async def delete_tenant(session, current_user, tenant_id: int):
    return await delete_tenant_service(session, tenant_id)

async def update_user(session: Session, id: int, tenant: TenantUpdate):
        return await update_user(session, id, tenant)
