from fastapi import APIRouter, Depends
from sqlmodel import Session
from database import get_session
from models.tenant import Tenant
from schemas.tenant_schema import TenantCreate, TenantRead, TenantUpdate
from controller.tenant import delete_tenant, update_tenant, create_tenant, get_all_tenant
from controller.permissions import AdminUser

router = APIRouter(prefix="/tenants", tags=["tenants"])

# todas as rotas de tenant: so admin

@router.delete("/{tenant_id}", response_model=TenantRead, status_code=200)
async def delete_tenant_route(
    tenant_id: int,
    current_user: AdminUser,
    session: Session = Depends(get_session)
):
    return await delete_tenant(session, tenant_id)

@router.put("/{id}")
async def update_tenant_route(id: int, tenant: TenantUpdate, current_user: AdminUser, session: Session = Depends(get_session)):
    return await update_tenant(session, id, tenant)

@router.post("/")
async def create(tenant: TenantCreate, current_user: AdminUser, session: Session = Depends(get_session)) -> Tenant:
    return await  create_tenant(session, tenant)

@router.get("/")
async def get_all(current_user: AdminUser, session: Session = Depends(get_session), id: int| None= None , skip: int = 0, limit: int | None = None):
    return await get_all_tenant(session, skip, limit, id)