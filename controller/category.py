from sqlmodel import Session

from controller.permissions import check_tenant_access, resolve_tenant_id
from models.category import Category
from models.user import User
from schemas.category import CategoryCreate, CategoryUpdate
from services.category import CategoryService


class CategoryController:

    async def create_category(session: Session, current_user: User, categoria: CategoryCreate) -> Category:
        check_tenant_access(current_user, categoria.tenant_id)  # criar: tenant do corpo
        return await CategoryService.create_category(session, categoria)

    async def get_all(
        session: Session,
        current_user: User,
        tenant_id: int | None = None,
        skip: int = 0,
        limit: int | None = None,
    ) -> list[Category]:
        tenant_id = resolve_tenant_id(current_user, tenant_id)  # listar
        return await CategoryService.get_all(session, tenant_id, skip, limit)

    async def get_category(session: Session, current_user: User, category_id: int) -> Category:
        category = await CategoryService.get_category_service(session, category_id)
        check_tenant_access(current_user, category.tenant_id)  # por id: tenant do registro
        return category

    async def update_category(
        session: Session, current_user: User, category_id: int, categoria: CategoryUpdate
    ) -> Category:
        await CategoryController.get_category(session, current_user, category_id)  # reaproveita a checagem
        return await CategoryService.update_category(session, category_id, categoria)

    async def delete_category(session: Session, current_user: User, category_id: int) -> None:
        await CategoryController.get_category(session, current_user, category_id)
        return await CategoryService.delete_category(session, category_id)
