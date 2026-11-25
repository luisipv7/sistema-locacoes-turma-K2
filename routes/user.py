from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from controller.permissions import AdminUser, StaffUser
from controller.user import UserController
from database import get_session
from schemas.auth import UserRead
from schemas.user import UserCreate, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])

# criar, editar e desativar: so admin
# consultar: admin e locador (o locador escolhe o cliente na hora da locacao)
# response_model=UserRead garante que o hashed_password nunca aparece na resposta


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create(user: UserCreate, current_user: AdminUser, session: Session = Depends(get_session)):
    return await UserController.create(session, user)


@router.get("/", response_model=list[UserRead])
async def get_all(
    current_user: StaffUser,
    tenant_id: int | None = None,
    skip: int = 0,
    limit: int | None = None,
    session: Session = Depends(get_session),
):
    return await UserController.get_all(session, current_user, tenant_id, skip, limit)


@router.get("/{id}", response_model=UserRead)
async def get_by_id(id: int, current_user: StaffUser, session: Session = Depends(get_session)):
    return await UserController.get_by_id(session, current_user, id)


@router.patch("/{id}", response_model=UserRead)
async def update_user(
    id: int, user: UserUpdate, current_user: AdminUser, session: Session = Depends(get_session)
):
    return await UserController.update_user(session, id, user)


@router.delete("/{id}", response_model=UserRead)
async def delete_user(id: int, current_user: AdminUser, session: Session = Depends(get_session)):
    return await UserController.delete_user(session, id)
