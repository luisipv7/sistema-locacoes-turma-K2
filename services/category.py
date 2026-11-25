from fastapi import HTTPException, status
from sqlmodel import Session, select

from models.category import Category
from models.item import Item
from models.tenant import Tenant
from schemas.category import CategoryCreate, CategoryUpdate


# ---------- funcoes auxiliares ----------

def _check_slug_available(
    session: Session, tenant_id: int, slug: str, ignore_id: int | None = None
) -> None:
    """O slug precisa ser unico dentro do tenant."""
    statement = select(Category).where(Category.tenant_id == tenant_id, Category.slug == slug)
    if ignore_id is not None:
        statement = statement.where(Category.id != ignore_id)
    if session.exec(statement).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ja existe uma categoria com esse slug",
        )


def _check_parent(session: Session, tenant_id: int, parent_id: int) -> None:
    """A categoria pai precisa existir e ser do mesmo tenant."""
    parent = session.get(Category, parent_id)
    if not parent or parent.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria pai nao encontrada",
        )


# ---------- CRUD ----------

class CategoryService:

    async def create_category(session: Session, categoria: CategoryCreate) -> Category:
        if not session.get(Tenant, categoria.tenant_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant nao encontrado")
        _check_slug_available(session, categoria.tenant_id, categoria.slug)
        if categoria.parent_id is not None:
            _check_parent(session, categoria.tenant_id, categoria.parent_id)

        new_category = Category(**categoria.model_dump(mode="json"))
        session.add(new_category)
        session.commit()
        session.refresh(new_category)
        return new_category

    async def get_all(
        session: Session,
        tenant_id: int,
        skip: int = 0,
        limit: int | None = None,
    ) -> list[Category]:
        statement = (
            select(Category)
            .where(Category.tenant_id == tenant_id)
            .order_by(Category.name)
            .offset(skip)
        )
        if limit is not None:
            statement = statement.limit(limit)
        return list(session.exec(statement).all())

    async def get_category_service(session: Session, category_id: int) -> Category:
        category = session.get(Category, category_id)
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria nao encontrada")
        return category

    async def update_category(session: Session, category_id: int, categoria: CategoryUpdate) -> Category:
        category = await CategoryService.get_category_service(session, category_id)

        # exclude_unset=True: pega SO os campos que vieram no corpo da requisicao
        changes = categoria.model_dump(exclude_unset=True)

        if "slug" in changes:
            _check_slug_available(session, category.tenant_id, changes["slug"], ignore_id=category.id)
        if changes.get("parent_id") is not None:
            if changes["parent_id"] == category.id:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Uma categoria nao pode ser pai dela mesma",
                )
            _check_parent(session, category.tenant_id, changes["parent_id"])

        category.sqlmodel_update(changes)
        session.add(category)
        session.commit()
        session.refresh(category)
        return category

    async def delete_category(session: Session, category_id: int) -> None:
        category = await CategoryService.get_category_service(session, category_id)

        # nao deixa apagar categoria que ainda tem itens ou subcategorias
        has_items = session.exec(select(Item).where(Item.category_id == category_id)).first()
        has_children = session.exec(select(Category).where(Category.parent_id == category_id)).first()
        if has_items or has_children:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Categoria em uso por itens ou subcategorias",
            )

        session.delete(category)
        session.commit()
