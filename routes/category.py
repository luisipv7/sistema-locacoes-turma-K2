from typing import Annotated
from fastapi import APIRouter, Depends
from sqlmodel import Session
from database import get_session
from schemas.category import CategoryCreate
from models.category import Category
from controller.category import CategoryController

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/")
async def create_task(categoria: CategoryCreate, session: Session = Depends(get_session)) -> Category:
    return await  CategoryController.create_category(session, categoria)

@router.delete("/{id}")
async def delete_task(id: int, session: Session = Depends(get_session)):
    return await CategoryController.delete_category(session, id)