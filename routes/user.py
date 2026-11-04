from fastapi import APIRouter, Depends
from sqlmodel import Session
from controller.user import UserController
from schemas.user import UserUpdate

from database import get_session

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.delete("/{id}")
async def delete_user(id: int, session: Session = Depends(get_session)):
    return await UserController.delete_user(session, id)

@router.put("/{id}")
async def update_user(id: int, user: UserUpdate, session: Session = Depends(get_session)):
    return await UserController.update_user(session, id, user)

@router.get("/{id}")
async def get_by_id(id: int, session: Session = Depends(get_session)):
    return await UserController.get_by_id(session, id)

@router.get("/")
async def get_all(session: Session = Depends(get_session), skip: int = 0, limit: int | None = None):
    return await UserController.get_all(session, skip, limit)