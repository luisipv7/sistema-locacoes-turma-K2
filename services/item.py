from fastapi import HTTPException, status
from sqlmodel import Session, select

from models.category import Category
from models.enums import UserRole
from models.item import Item
from models.tenant import Tenant
from models.user import User
from schemas.item_schema import ItemCreate, ItemUpdate


# ---------- funcoes auxiliares ----------

def _check_slug_available(
    session: Session, tenant_id: int, slug: str, ignore_id: int | None = None
) -> None:
    statement = select(Item).where(Item.tenant_id == tenant_id, Item.slug == slug)
    if ignore_id is not None:
        statement = statement.where(Item.id != ignore_id)
    if session.exec(statement).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ja existe um item com esse slug",
        )


def _check_category(session: Session, tenant_id: int, category_id: int) -> None:
    """A categoria precisa existir E ser do mesmo tenant do item."""
    category = session.get(Category, category_id)
    if not category or category.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria nao encontrada")


def _check_owner(session: Session, tenant_id: int, owner_id: int) -> None:
    """O dono do item precisa ser um locador do mesmo tenant."""
    owner = session.get(User, owner_id)
    if not owner or owner.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dono do item nao encontrado")
    if owner.role != UserRole.LOCADOR:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Somente um locador pode ser dono de item",
        )


# ---------- CRUD ----------

class ItemService:

    async def create(session: Session, item: ItemCreate) -> Item:
        if not session.get(Tenant, item.tenant_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant nao encontrado")
        _check_slug_available(session, item.tenant_id, item.slug)
        if item.category_id is not None:
            _check_category(session, item.tenant_id, item.category_id)
        if item.owner_id is not None:
            _check_owner(session, item.tenant_id, item.owner_id)

        new_item = Item(**item.model_dump())
        session.add(new_item)
        session.commit()
        session.refresh(new_item)
        return new_item

    async def get_all_items(
        session: Session,
        tenant_id: int,
        category_id: int | None = None,
        skip: int = 0,
        limit: int | None = None,
    ) -> list[Item]:
        statement = select(Item).where(Item.tenant_id == tenant_id)
        if category_id is not None:  # filtro opcional
            statement = statement.where(Item.category_id == category_id)
        statement = statement.order_by(Item.name).offset(skip)
        if limit is not None:
            statement = statement.limit(limit)
        return list(session.exec(statement).all())

    async def get_by_id(session: Session, id: int) -> Item:
        item = session.get(Item, id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item nao encontrado")
        return item

    async def update(session: Session, id: int, item: ItemUpdate) -> Item:
        db_item = await ItemService.get_by_id(session, id)
        changes = item.model_dump(exclude_unset=True)

        if "slug" in changes:
            _check_slug_available(session, db_item.tenant_id, changes["slug"], ignore_id=db_item.id)
        if changes.get("category_id") is not None:
            _check_category(session, db_item.tenant_id, changes["category_id"])
        if changes.get("owner_id") is not None:
            _check_owner(session, db_item.tenant_id, changes["owner_id"])

        db_item.sqlmodel_update(changes)
        session.add(db_item)
        session.commit()
        session.refresh(db_item)
        return db_item

    async def delete_by_id(session: Session, id: int) -> Item:
        """Nao apaga: o item tem historico de locacoes. So desativa."""
        item = await ItemService.get_by_id(session, id)
        item.is_active = False
        session.add(item)
        session.commit()
        session.refresh(item)
        return item
