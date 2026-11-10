from http.client import HTTPException

from models.item import Item
from schemas.item_schema import ItemCreate, ItemUpdate
from sqlmodel import Session, select
from models.item import Item

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

        session.delete(item)
        session.commit()
        return {"message": "Item deleted successfully"}
    

    async def update(session: Session, id: int, user: ItemUpdate):
        db_item = session.get(Item, id)
        if db_item is None:
            raise HTTPException(status_code=404, detail="Item not found")

        user_data = user.model_dump(mode="json", exclude_unset=True)

        
        for field, value in user_data.items():
            setattr(db_item, field, value)

        session.add(db_item)
        session.commit()
        session.refresh(db_item)
        return {"message": "Item atualizado com sucesso "}

    async def create(session: Session, item: ItemCreate) -> Item:
        new_item = Item(**item.model_dump(mode="json"))
        session.add(new_item)
        session.commit()
        session.refresh(new_item)
        return new_item