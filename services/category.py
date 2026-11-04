from select import select

from fastapi import HTTPException

from models.category import Item
from schemas.category import CategoryCreate
from sqlmodel import Session

class CategoryService:

    async def create_category(session: Session, categoria: CategoryCreate) -> Item:
        new_category = Item(**categoria.model_dump(mode="json"))
        session.add(new_category)
        session.commit()
        session.refresh(new_category)
        return new_category


    async def delete_category(session: Session, id: int):
        category = session.get(Item, id)
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
            statement = select(Item)
    
            statement = statement.offset(skip)
            if limit is not None:
                statement = statement.limit(limit)
    
            return session.exec(statement).all()