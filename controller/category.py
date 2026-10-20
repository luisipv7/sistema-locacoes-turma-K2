from schemas.category import CategoryCreate
from services.category import create_category_service
from models.category import Category

from sqlmodel import Session
from database import get_session


async def create_category(session: Session, categoria: CategoryCreate) -> Category:
    return await create_category_service(session, categoria)