from fastapi import HTTPException, status

from models.category import Category
from models.tenant import Tenant
from schemas.category import CategoryCreate
from sqlmodel import Session, select

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

class CategoryService:

    async def create_category(session: Session, categoria: CategoryCreate) -> Category:

        if not session.get(Tenant, categoria.tenant_id):
            raise HTTPException(status_code=404, detail="Tenant nao encontrado")
        _check_slug_available(session, categoria.tenant_id, categoria.slug)
        if categoria.parent_id is not None:
            _check_parent(session, categoria.tenant_id, categoria.parent_id)

        new_category = Category(**categoria.model_dump(mode="json"))
        session.add(new_category)
        session.commit()
        session.refresh(new_category)
        return new_category


    async def delete_category(session: Session, id: int):
        category = session.get(Category, id)
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found")

        session.delete(category)
        session.commit()
        return {"message": "Category deleted successfully"}

    async def get_all(
            session: Session,
            skip: int = 0,
            limit: int | None = None,
        ):
            statement = select(Category)
    
            statement = statement.offset(skip)
            if limit is not None:
                statement = statement.limit(limit)
    
            return session.exec(statement).all()