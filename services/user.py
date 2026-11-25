from fastapi import HTTPException, status
from sqlmodel import Session, select

from models.tenant import Tenant
from models.user import User
from schemas.user import UserCreate, UserUpdate
from security import get_password_hash


def _check_username_available(
    session: Session, username: str, ignore_id: int | None = None
) -> None:
    """Username unico no sistema todo: o login busca so pelo username."""
    statement = select(User).where(User.username == username)
    if ignore_id is not None:
        statement = statement.where(User.id != ignore_id)
    if session.exec(statement).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ja existe um usuario com esse username",
        )


class UserService:

    async def create(session: Session, user: UserCreate) -> User:
        if not session.get(Tenant, user.tenant_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant nao encontrado")
        _check_username_available(session, user.username)

        new_user = User(
            tenant_id=user.tenant_id,
            username=user.username,
            hashed_password=get_password_hash(user.password),  # NUNCA salve a senha pura
            role=user.role,
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user

    async def get_all(
        session: Session,
        tenant_id: int,
        skip: int = 0,
        limit: int | None = None,
    ) -> list[User]:
        statement = (
            select(User)
            .where(User.tenant_id == tenant_id)
            .order_by(User.username)
            .offset(skip)
        )
        if limit is not None:
            statement = statement.limit(limit)
        return list(session.exec(statement).all())

    async def get_by_id(session: Session, id: int) -> User:
        user = session.get(User, id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario nao encontrado")
        return user

    async def update_user(session: Session, id: int, user: UserUpdate) -> User:
        db_user = await UserService.get_by_id(session, id)
        changes = user.model_dump(exclude_unset=True)

        if "username" in changes:
            _check_username_available(session, changes["username"], ignore_id=db_user.id)

        # a senha nao vai direto: tira do dicionario e grava o hash
        password = changes.pop("password", None)
        if password:
            db_user.hashed_password = get_password_hash(password)

        db_user.sqlmodel_update(changes)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user

    async def delete_user(session: Session, id: int) -> User:
        """Nao apaga: o usuario pode ter locacoes. So desativa (o login ja recusa inativo)."""
        db_user = await UserService.get_by_id(session, id)
        db_user.is_active = False
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user
