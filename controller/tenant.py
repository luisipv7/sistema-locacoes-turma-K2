from services.tenant import delete_tenant_service

async def delete_tenant(session, current_user, tenant_id: int):
    return await delete_tenant_service(session, tenant_id)