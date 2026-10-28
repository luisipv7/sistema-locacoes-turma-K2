from models.category import Category
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


    