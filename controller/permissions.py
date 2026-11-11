from typing import Annotated, Callable

from fastapi import Depends, HTTPException, status

from controller.auth import get_current_user
from models.enums import UserRole
from models.user import User

# qualquer usuario logado
CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*roles: UserRole) -> Callable[[User], User]:
    """Cria uma dependencia que so deixa passar os papeis informados."""

    def dependency(current_user: CurrentUser) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Voce nao tem permissao para esta acao",
            )
        return current_user

    return dependency


# use estes tipos nos parametros das rotas
AdminUser = Annotated[User, Depends(require_roles(UserRole.ADMIN))]
StaffUser = Annotated[User, Depends(require_roles(UserRole.ADMIN, UserRole.LOCADOR))]
ClienteUser = Annotated[User, Depends(require_roles(UserRole.CLIENTE))]


def check_tenant_access(user: User, tenant_id: int) -> None:
    """Admin acessa qualquer tenant; locador e cliente, so o proprio."""
    if user.role == UserRole.ADMIN:
        return
    if user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Voce so pode acessar dados do seu tenant",
        )


def resolve_tenant_id(user: User, tenant_id: int | None) -> int:
    """Descobre de qual tenant listar. Locador e cliente: o dele. Admin: precisa informar."""
    if user.role == UserRole.ADMIN:
        if tenant_id is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Informe o tenant_id",
            )
        return tenant_id
    check_tenant_access(user, tenant_id if tenant_id is not None else user.tenant_id)
    return user.tenant_id
