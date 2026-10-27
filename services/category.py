from models.category import Category
from schemas.category import CategoryCreate
from sqlmodel import Session

class CategoryService:

    async def create_category(session: Session, categoria: CategoryCreate) -> Category:
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