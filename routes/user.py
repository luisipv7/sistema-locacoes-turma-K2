from fastapi import APIRouter, Depends
from sqlmodel import Session
from controller.user import UserController
from models.user import User
from schemas.user import UserCreate, UserUpdate
from controller.permissions import AdminUser, StaffUser

from database import get_session

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

# criar, editar e desativar: so admin
# consultar: admin e locador (o locador escolhe o cliente na hora da locacao)

@router.delete("/{id}")
async def delete_user(id: int, current_user: AdminUser, session: Session = Depends(get_session)):
    return await UserController.delete_user(session, id)

@router.put("/{id}")
async def update_user(id: int, user: UserUpdate, current_user: AdminUser, session: Session = Depends(get_session)):
    return await UserController.update_user(session, id, user)

@router.get("/{id}")
async def get_by_id(id: int, current_user: StaffUser, session: Session = Depends(get_session)):
    return await UserController.get_by_id(session, id)

@router.get("/")
async def get_all(current_user: StaffUser, session: Session = Depends(get_session), skip: int = 0, limit: int | None = None):
    return await UserController.get_all(session, skip, limit)

@router.post("/")
async def create(user: UserCreate, current_user: AdminUser, session: Session = Depends(get_session)) -> User:
    return await  UserController.create(session, user)