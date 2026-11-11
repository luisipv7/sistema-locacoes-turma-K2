from fastapi import APIRouter, Depends
from sqlmodel import Session
from database import get_session
from schemas.tenant_schema import TenantRead, TenantUpdate
from controller.tenant import delete_tenant, update_tenant
# from security import AdminUser 

router = APIRouter(prefix="/tenants", tags=["tenants"])

@router.delete("/{tenant_id}", response_model=TenantRead, status_code=200)
async def delete_tenant_route(
    tenant_id: int, 
    # current_user: AdminUser, 
    session: Session = Depends(get_session)
):
    return await delete_tenant(session, current_user, tenant_id)

@router.put("/{id}")
async def update_tenant(id: int, tenant: TenantUpdate, session: Session = Depends(get_session)):
    return await update_tenant(session, id, tenant)

@router.post("/")
async def create(tenant: TenantCreate, session: Session = Depends(get_session)) -> Tenant:
    return await  create(session, tenant)

@router.get("/")
async def get_all(session: Session = Depends(get_session), skip: int = 0, limit: int | None = None):
    return await get_all(session, skip, limit)