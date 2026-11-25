from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from controller.item import ItemController
from controller.permissions import CurrentUser, StaffUser
from database import get_session
from schemas.item_schema import ItemCreate, ItemRead, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])

# criar, editar e apagar: admin e locador
# consultar: qualquer usuario logado (o cliente precisa ver para escolher o que alugar)


@router.post("/", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
async def create(item: ItemCreate, current_user: StaffUser, session: Session = Depends(get_session)):
    return await ItemController.create(session, current_user, item)


@router.get("/", response_model=list[ItemRead])
async def get_all(
    current_user: CurrentUser,
    tenant_id: int | None = None,
    category_id: int | None = None,
    skip: int = 0,
    limit: int | None = None,
    session: Session = Depends(get_session),
):
    return await ItemController.get_all_items(session, current_user, tenant_id, category_id, skip, limit)


@router.get("/{id}", response_model=ItemRead)
async def get_by_id(id: int, current_user: CurrentUser, session: Session = Depends(get_session)):
    return await ItemController.get_by_id(session, current_user, id)


@router.patch("/{id}", response_model=ItemRead)
async def update(
    id: int, item: ItemUpdate, current_user: StaffUser, session: Session = Depends(get_session)
):
    return await ItemController.update(session, current_user, id, item)


@router.delete("/{id}", response_model=ItemRead)
async def delete_by_id(id: int, current_user: StaffUser, session: Session = Depends(get_session)):
    return await ItemController.delete_by_id(session, current_user, id)
