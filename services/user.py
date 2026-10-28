from fastapi import HTTPException
from sqlmodel import Session, select
from schemas.user import UserUpdate

from models.user import User
from security import get_password_hash

class UserService:

    async def delete_user(session: Session, id: int):
        user = session.get(User, id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        session.delete(user)
        session.commit()
        return {"message": "Usuário deletado com sucesso "}

    
    async def update_user(session: Session, id: int, user: UserUpdate):
        db_user = session.get(User, id)
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        user_data = user.model_dump(mode="json", exclude_unset=True)

        password = user_data.pop("password", None)
        if password:
            user_data["hashed_password"] = get_password_hash(password)

        for field, value in user_data.items():
            setattr(db_user, field, value)

        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return {"message": "Usuário atualizado com sucesso "}
    