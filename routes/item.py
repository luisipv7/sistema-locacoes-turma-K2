from typing import Annotated
from fastapi import APIRouter, Depends
from models.item import Item
from schemas.item_schema import ItemCreate, ItemUpdate
from sqlmodel import Session
from database import get_session
from controller.item import ItemController
from controller.permissions import CurrentUser, StaffUser


router = APIRouter(prefix="/items", tags=["items"])

# criar, editar e apagar: admin e locador
# consultar: qualquer usuario logado (o cliente precisa ver para escolher o que alugar)


@router.get("/")
async def get_all(current_user: CurrentUser, session: Session = Depends(get_session), skip: int = 0, limit: int | None = None, ):
    return await ItemController.get_all_items(session, skip, limit)


@router.delete("/{id}")
async def delete_by_id(id: int, current_user: StaffUser, session: Session = Depends(get_session)):
    return await ItemController.delete_by_id(session, id)

@router.put("/{id}")
async def update(id: int, user: ItemUpdate, current_user: StaffUser, session: Session = Depends(get_session)):
    return await ItemController.update(session, id, user)

@router.post("/")
async def create(item: ItemCreate, current_user: StaffUser, session: Session = Depends(get_session)) -> Item:
    return await  ItemController.create(session, item)