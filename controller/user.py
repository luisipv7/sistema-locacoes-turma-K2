from services.user import UserService
from schemas.user import UserUpdate

from sqlmodel import Session
from database import get_session

class UserController:

    async def delete_user(session: Session, id: int):
        return await UserService.delete_user(session, id)

    async def update_user(session: Session, id: int, user: UserUpdate):
        return await UserService.update_user(session, id, user)
    