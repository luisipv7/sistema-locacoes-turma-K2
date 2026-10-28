from services.item import ItemService
from models.item import Item

from sqlmodel import Session
from database import get_session
class CategoryController:

    async def get_all_items(session: Session, skip: int = 0, limit: int | None = None) -> Item:
        return await ItemService.get_all_items(session, skip, limit)