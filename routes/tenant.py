from fastapi import APIRouter, Depends
from sqlmodel import Session
from database import get_session
from schemas.tenant_schema import TenantRead
from controller.tenant import delete_tenant
# from security import AdminUser 

router = APIRouter(prefix="/tenants", tags=["tenants"])

@router.delete("/{tenant_id}", response_model=TenantRead, status_code=200)
async def delete_tenant_route(
    tenant_id: int, 
    # current_user: AdminUser, 
    session: Session = Depends(get_session)
):
    return await delete_tenant(session, current_user, tenant_id)