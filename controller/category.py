from controller.permissions import StaffUser, check_tenant_access
from schemas.category import CategoryCreate
from services.category import CategoryService
from models.category import Category

from sqlmodel import Session
from database import get_session
class CategoryController:


    async def create_category(session: Session, current_user: StaffUser , categoria: CategoryCreate) -> Category:
        check_tenant_access(current_user, categoria.tenant_id)  
        return await CategoryService.create_category(session, categoria)
    
    async def delete_category(session: Session, id: int):
        return await CategoryService.delete_category(session, id)

    async def get_all(session: Session, skip: int = 0, limit: int | None = None) -> list[Category]:
        return await CategoryService.get_all(session, skip, limit)
    