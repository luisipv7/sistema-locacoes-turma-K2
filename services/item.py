from http.client import HTTPException

from models.category import Category
from schemas.category import CategoryCreate
from sqlmodel import Session, select
from models.item import Category

class ItemService:

    async def get_all_items(
        session: Session,
        skip: int = 0,
        limit: int | None = None,
    ):
        statement = select(Category)

        statement = statement.offset(skip)
        if limit is not None:
            statement = statement.limit(limit)

        return session.exec(statement).all()

    async def delete_by_id(session: Session, id: int):
        item = session.get(Category, id)
        if item is None:
            raise HTTPException(status_code=404, detail="Item not found")

        session.delete(item)
        session.commit()
        return {"message": "Item deleted successfully"}
    