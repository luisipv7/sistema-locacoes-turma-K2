from sqlmodel import Session

from controller.permissions import check_tenant_access, resolve_tenant_id
from models.item import Item
from models.user import User
from schemas.item_schema import ItemCreate, ItemUpdate
from services.item import ItemService


class ItemController:

    async def create(session: Session, current_user: User, item: ItemCreate) -> Item:
        check_tenant_access(current_user, item.tenant_id)  # criar: tenant do corpo
        return await ItemService.create(session, item)

    async def get_all_items(
        session: Session,
        current_user: User,
        tenant_id: int | None = None,
        category_id: int | None = None,
        skip: int = 0,
        limit: int | None = None,
    ) -> list[Item]:
        tenant_id = resolve_tenant_id(current_user, tenant_id)  # listar
        return await ItemService.get_all_items(session, tenant_id, category_id, skip, limit)

    async def get_by_id(session: Session, current_user: User, id: int) -> Item:
        item = await ItemService.get_by_id(session, id)
        check_tenant_access(current_user, item.tenant_id)  # por id: tenant do registro
        return item

    async def update(session: Session, current_user: User, id: int, item: ItemUpdate) -> Item:
        await ItemController.get_by_id(session, current_user, id)
        return await ItemService.update(session, id, item)

    async def delete_by_id(session: Session, current_user: User, id: int) -> Item:
        await ItemController.get_by_id(session, current_user, id)
        return await ItemService.delete_by_id(session, id)
