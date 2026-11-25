from fastapi import HTTPException, status
from sqlmodel import Session

from controller.permissions import check_tenant_access, resolve_tenant_id
from models.enums import UserRole
from models.user import User
from schemas.user import UserCreate, UserUpdate
from services.user import UserService

# o admin nao cria outro admin pela API (o unico admin vem do db01.sql)
CREATABLE_ROLES = (UserRole.LOCADOR, UserRole.CLIENTE)


def _check_role(role: UserRole | None) -> None:
    if role is not None and role not in CREATABLE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="O admin so cria usuarios locador ou cliente",
        )


class UserController:

    async def create(session: Session, user: UserCreate) -> User:
        _check_role(user.role)
        return await UserService.create(session, user)

    async def get_all(
        session: Session,
        current_user: User,
        tenant_id: int | None = None,
        skip: int = 0,
        limit: int | None = None,
    ) -> list[User]:
        tenant_id = resolve_tenant_id(current_user, tenant_id)
        return await UserService.get_all(session, tenant_id, skip, limit)

    async def get_by_id(session: Session, current_user: User, id: int) -> User:
        user = await UserService.get_by_id(session, id)
        check_tenant_access(current_user, user.tenant_id)
        return user

    async def update_user(session: Session, id: int, user: UserUpdate) -> User:
        _check_role(user.role)
        return await UserService.update_user(session, id, user)

    async def delete_user(session: Session, id: int) -> User:
        return await UserService.delete_user(session, id)
