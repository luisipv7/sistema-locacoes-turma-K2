from http.client import HTTPException

from models.category import Category
from models.enums import UserRole
from models.item import Item
from models.tenant import Tenant
from models.user import User
from schemas.item_schema import ItemCreate, ItemUpdate
from sqlmodel import Session, select
from models.item import Item

def _check_slug_available(
    session: Session, tenant_id: int, slug: str, ignore_id: int | None = None
) -> None:
    statement = select(Item).where(Item.tenant_id == tenant_id, Item.slug == slug)
    if ignore_id is not None:
        statement = statement.where(Item.id != ignore_id)
    if session.exec(statement).first():
        raise HTTPException(
            status_code=409,
            detail="Ja existe um item com esse slug",
        )

def _check_category(session: Session, tenant_id: int, category_id: int) -> None:
    """A categoria precisa existir E ser do mesmo tenant do item."""
    category = session.get(Category, category_id)
    if not category or category.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Categoria nao encontrada")


def _check_owner(session: Session, tenant_id: int, owner_id: int) -> None:
    """O dono do item precisa ser um locador do mesmo tenant."""
    owner = session.get(User, owner_id)
    if not owner or owner.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Dono do item nao encontrado")
    if owner.role != UserRole.LOCADOR:
        raise HTTPException(
            status_code=422,
            detail="Somente um locador pode ser dono de item",
        )

class ItemService:

    async def get_all_items(
        session: Session,
        skip: int = 0,
        limit: int | None = None,
    ):
        statement = select(Item)

        statement = statement.offset(skip)
        if limit is not None:
            statement = statement.limit(limit)

        return session.exec(statement).all()

    async def delete_by_id(session: Session, id: int):
        item = session.get(Item, id)
        if item is None:
            raise HTTPException(status_code=404, detail="Item not found")

        item.is_active = False
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"message": "Item deleted successfully"}
    

    async def update(session: Session, id: int, user: ItemUpdate):
        db_item = session.get(Item, id)
        if db_item is None:
            raise HTTPException(status_code=404, detail="Item not found")

        user_data = user.model_dump(mode="json", exclude_unset=True)

        if "slug" in user_data:
            _check_slug_available(session, db_item.tenant_id, user_data["slug"], ignore_id=db_item.id)
        if user_data.get("category_id") is not None:
            _check_category(session, db_item.tenant_id, user_data["category_id"])
        if user_data.get("owner_id") is not None:
            _check_owner(session, db_item.tenant_id, user_data["owner_id"])
        
        for field, value in user_data.items():
            setattr(db_item, field, value)

        session.add(db_item)
        session.commit()
        session.refresh(db_item)
        return {"message": "Item atualizado com sucesso "}

    async def create(session: Session, item: ItemCreate) -> Item:

        if not session.get(Tenant, item.tenant_id):
            raise HTTPException(status_code=404, detail="Tenant nao encontrado")
        _check_slug_available(session, item.tenant_id, item.slug)
        if item.category_id is not None:
            _check_category(session, item.tenant_id, item.category_id)
        if item.owner_id is not None:
            _check_owner(session, item.tenant_id, item.owner_id)

        new_item = Item(**item.model_dump(mode="json"))
        session.add(new_item)
        session.commit()
        session.refresh(new_item)
        return new_item