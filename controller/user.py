from services.user import UserService

from sqlmodel import Session
from database import get_session

class UserController:

    async def delete_user(session: Session, id: int):
        return await UserService.delete_user(session, id)