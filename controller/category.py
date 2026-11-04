from schemas.category import CategoryCreate
from services.category import CategoryService
from models.category import Item

from sqlmodel import Session
from database import get_session
class CategoryController:


    async def create_category(session: Session, categoria: CategoryCreate) -> Item:
        return await CategoryService.create_category(session, categoria)
    
    async def delete_category(session: Session, id: int):
        return await CategoryService.delete_category(session, id)

    async def get_all(session: Session, skip: int = 0, limit: int | None = None) -> Item:
        return await CategoryService.get_all(session, skip, limit)
    