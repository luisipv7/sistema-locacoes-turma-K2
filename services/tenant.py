from sqlmodel import Session, select
from models.tenant import Tenant, TenantStatus
from fastapi import HTTPException

from schemas.tenant_schema import TenantCreate, TenantUpdate

def _check_slug_available(session: Session, slug: str, ignore_id: int | None = None) -> None:
    """No tenant o slug e unico no sistema inteiro."""
    statement = select(Tenant).where(Tenant.slug == slug)
    if ignore_id is not None:
        statement = statement.where(Tenant.id != ignore_id)
    if session.exec(statement).first():
        raise HTTPException(
            status_code=409,
            detail="Ja existe um tenant com esse slug",
        )

async def get_tenant_service(session: Session, tenant_id: int):
    tenant = session.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")
    return tenant

async def delete_tenant_service(session: Session, tenant_id: int):
    tenant = await get_tenant_service(session, tenant_id)
    tenant.status = TenantStatus.INACTIVE
    session.add(tenant)
    session.commit()
    session.refresh(tenant)
    return tenant

async def update_tenant_service(session: Session, id: int, tenant: TenantUpdate):
        db_tenant = session.get(Tenant, id)
        if db_tenant is None:
            raise HTTPException(status_code=404, detail="Tenant not found")

        tenant_data = tenant.model_dump(mode="json", exclude_unset=True)

        for field, value in tenant_data.items():
            setattr(db_tenant, field, value)

        session.add(db_tenant)
        session.commit()
        session.refresh(db_tenant)
        return {"message": "Usuário atualizado com sucesso "}

async def create_tenant_service(session: Session, tenant: TenantCreate) -> Tenant:
        _check_slug_available(session, tenant.slug)
        new_tenant = Tenant(**tenant.model_dump(mode="json"))
        session.add(new_tenant)
        session.commit()
        session.refresh(new_tenant)
        return new_tenant

async def get_all_tenant_service(
            session: Session,
            skip: int = 0,
            limit: int | None = None,
            id: int | None = None
        ):
            if id is not None:
                tenant = session.get(Tenant, id)
                return tenant
            statement = select(Tenant)
    
            statement = statement.offset(skip)
            if limit is not None:
                statement = statement.limit(limit)
    
            return session.exec(statement).all()