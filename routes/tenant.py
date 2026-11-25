from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from controller.permissions import AdminUser
from controller.tenant import create_tenant, delete_tenant, get_all_tenant, get_tenant, update_tenant
from database import get_session
from schemas.tenant_schema import TenantCreate, TenantRead, TenantUpdate

router = APIRouter(prefix="/tenants", tags=["tenants"])

# todas as rotas de tenant: so admin


@router.post("/", response_model=TenantRead, status_code=status.HTTP_201_CREATED)
async def create(tenant: TenantCreate, current_user: AdminUser, session: Session = Depends(get_session)):
    return await create_tenant(session, tenant)


@router.get("/", response_model=list[TenantRead])
async def get_all(
    current_user: AdminUser,
    skip: int = 0,
    limit: int | None = None,
    session: Session = Depends(get_session),
):
    return await get_all_tenant(session, skip, limit)


@router.get("/{tenant_id}", response_model=TenantRead)
async def get_tenant_route(tenant_id: int, current_user: AdminUser, session: Session = Depends(get_session)):
    return await get_tenant(session, tenant_id)


@router.patch("/{tenant_id}", response_model=TenantRead)
async def update_tenant_route(
    tenant_id: int, tenant: TenantUpdate, current_user: AdminUser, session: Session = Depends(get_session)
):
    return await update_tenant(session, tenant_id, tenant)


# o DELETE devolve o tenant (com status "inactive"), ja que ele continua existindo
@router.delete("/{tenant_id}", response_model=TenantRead)
async def delete_tenant_route(tenant_id: int, current_user: AdminUser, session: Session = Depends(get_session)):
    return await delete_tenant(session, tenant_id)
