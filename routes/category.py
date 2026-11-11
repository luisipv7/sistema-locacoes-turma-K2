from typing import Annotated
from fastapi import APIRouter, Depends
from sqlmodel import Session
from database import get_session
from schemas.category import CategoryCreate
from models.category import Category
from controller.category import CategoryController
from controller.permissions import CurrentUser, StaffUser

router = APIRouter(prefix="/categories", tags=["categories"])

# criar, editar e apagar: admin e locador
# consultar: qualquer usuario logado (o cliente precisa ver para escolher o que alugar)


@router.post("/")
async def create_category(categoria: CategoryCreate, current_user: StaffUser, session: Session = Depends(get_session)) -> Category:
    return await  CategoryController.create_category(session, current_user, categoria)

@router.delete("/{id}")
async def delete_category(id: int, current_user: StaffUser, session: Session = Depends(get_session)):
    return await CategoryController.delete_category(session, id)

@router.get("/")
async def get_all(current_user: CurrentUser, session: Session = Depends(get_session), skip: int = 0, limit: int | None = None):
    return await CategoryController.get_all(session, skip, limit)