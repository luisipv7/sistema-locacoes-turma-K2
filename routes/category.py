from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from controller.category import CategoryController
from controller.permissions import CurrentUser, StaffUser
from database import get_session
from schemas.category import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])

# criar, editar e apagar: admin e locador
# consultar: qualquer usuario logado (o cliente precisa ver para escolher o que alugar)


@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    categoria: CategoryCreate, current_user: StaffUser, session: Session = Depends(get_session)
):
    return await CategoryController.create_category(session, current_user, categoria)


@router.get("/", response_model=list[CategoryRead])
async def get_all(
    current_user: CurrentUser,
    tenant_id: int | None = None,
    skip: int = 0,
    limit: int | None = None,
    session: Session = Depends(get_session),
):
    return await CategoryController.get_all(session, current_user, tenant_id, skip, limit)


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(
    category_id: int, current_user: CurrentUser, session: Session = Depends(get_session)
):
    return await CategoryController.get_category(session, current_user, category_id)


@router.patch("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: int,
    categoria: CategoryUpdate,
    current_user: StaffUser,
    session: Session = Depends(get_session),
):
    return await CategoryController.update_category(session, current_user, category_id, categoria)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int, current_user: StaffUser, session: Session = Depends(get_session)
):
    await CategoryController.delete_category(session, current_user, category_id)
