from fastapi import HTTPException
from sqlmodel import Session, select

from models.user import User

class UserService:

    async def delete_user(session: Session, id: int):
        user = session.get(User, id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        session.delete(user)
        session.commit()
        return {"message": "Usuário deletado com sucesso "}