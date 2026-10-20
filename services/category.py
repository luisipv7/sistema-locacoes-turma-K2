from models.category import Category
from schemas.category import CategoryCreate
from sqlmodel import Session


async def create_category_service(session: Session, categoria: CategoryCreate) -> Category:
    new_category = Category(**categoria.model_dump(mode="json"))
    session.add(new_category)
    session.commit()
    session.refresh(new_category)
    return new_category