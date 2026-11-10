from services.item import ItemService
from models.item import Item
from schemas.item_schema import ItemCreate, ItemUpdate

from sqlmodel import Session
from database import get_session
class ItemController:

    async def get_all_items(session: Session, skip: int = 0, limit: int | None = None) -> Item:
        return await ItemService.get_all_items(session, skip, limit)

    async def delete_by_id(session: Session, id: int):
        return await ItemService.delete_by_id(session, id)

    async def update(session: Session, id: int, user: ItemUpdate):
        return await ItemService.update(session, id, user)

    async def create(session: Session, item: ItemCreate) -> Item:
            return await ItemService.create(session, item)