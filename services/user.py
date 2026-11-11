from fastapi import HTTPException
from sqlmodel import Session, select
from models.tenant import Tenant
from schemas.user import UserCreate, UserUpdate

from models.user import User
from security import get_password_hash

def _check_username_available(
    session: Session, username: str, ignore_id: int | None = None
) -> None:
    statement = select(User).where(User.username == username)
    if ignore_id is not None:
        statement = statement.where(User.id != ignore_id)
    if session.exec(statement).first():
        raise HTTPException(
            status_code=409,
            detail="Ja existe um usuario com esse username",
        )


class UserService:

    async def delete_user(session: Session, id: int):
        user = session.get(User, id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        user.is_active = False
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    
    async def update_user(session: Session, id: int, user: UserUpdate):
        db_user = session.get(User, id)
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        user_data = user.model_dump(mode="json", exclude_unset=True)

        ## Isto foi feito para verioficar se o usuario envio o campo de senha
        password = user_data.pop("password", None)
        ## Aqui ele valida se exite realmente algum dado
        if password:
            ## Aqui ele criptografa a senha exemplo você enviou: 123 aqui ele passa esse 123 para "pbkdf2_sha256$......"
            user_data["hashed_password"] = get_password_hash(password)

        for field, value in user_data.items():
            setattr(db_user, field, value)

        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return {"message": "Usuário atualizado com sucesso "}

    async def get_by_id(session: Session, id: int):
        user = session.get(User, id)
        if user is None:
            raise HTTPException(status_code=404, detail="user not found")
        return user 

    async def get_all(
        session: Session,
        skip: int = 0,
        limit: int | None = None,
    ):
        statement = select(User)

        statement = statement.offset(skip)
        if limit is not None:
            statement = statement.limit(limit)

        return session.exec(statement).all()

    async def create(session: Session, user: UserCreate) -> User:
        if not session.get(Tenant, user.tenant_id):
            raise HTTPException(status_code=404, detail="Tenant nao encontrado")
        _check_username_available(session, user.username)
        new_user = User(**user.model_dump(mode="json"))
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user
