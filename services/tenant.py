from sqlmodel import Session
from models.tenant import Tenant, TenantStatus
from fastapi import HTTPException

from schemas.tenant_schema import TenantUpdate

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

async def update_tenant(session: Session, id: int, tenant: TenantUpdate):
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