from http.client import HTTPException

from models.category import Item
from schemas.category import CategoryCreate
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
    