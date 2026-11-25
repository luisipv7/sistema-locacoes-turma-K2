from fastapi import HTTPException, status
from sqlmodel import Session, select

from models.enums import TenantStatus
from models.tenant import Tenant
from schemas.tenant_schema import TenantCreate, TenantUpdate


def _check_slug_available(session: Session, slug: str, ignore_id: int | None = None) -> None:
    """No tenant o slug e unico no sistema inteiro."""
    statement = select(Tenant).where(Tenant.slug == slug)
    if ignore_id is not None:
        statement = statement.where(Tenant.id != ignore_id)
    if session.exec(statement).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ja existe um tenant com esse slug",
        )


async def create_tenant_service(session: Session, tenant: TenantCreate) -> Tenant:
    _check_slug_available(session, tenant.slug)
    new_tenant = Tenant(**tenant.model_dump())
    session.add(new_tenant)
    session.commit()
    session.refresh(new_tenant)
    return new_tenant


async def get_all_tenant_service(
    session: Session, skip: int = 0, limit: int | None = None
) -> list[Tenant]:
    statement = select(Tenant).order_by(Tenant.name).offset(skip)
    if limit is not None:
        statement = statement.limit(limit)
    return list(session.exec(statement).all())


async def get_tenant_service(session: Session, tenant_id: int) -> Tenant:
    tenant = session.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant nao encontrado")
    return tenant


async def update_tenant_service(session: Session, tenant_id: int, data: TenantUpdate) -> Tenant:
    tenant = await get_tenant_service(session, tenant_id)
    changes = data.model_dump(exclude_unset=True)

    if "slug" in changes:
        _check_slug_available(session, changes["slug"], ignore_id=tenant.id)

    tenant.sqlmodel_update(changes)
    session.add(tenant)
    session.commit()
    session.refresh(tenant)
    return tenant


async def delete_tenant_service(session: Session, tenant_id: int) -> Tenant:
    """Nao apaga de verdade: o tenant tem usuarios, itens e locacoes. So desativa."""
    tenant = await get_tenant_service(session, tenant_id)
    tenant.status = TenantStatus.INACTIVE
    session.add(tenant)
    session.commit()
    session.refresh(tenant)
    return tenant
