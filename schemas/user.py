# /schemas/user.py

from sqlmodel import Field, SQLModel

from models.enums import UserRole
from schemas.auth import UserRead  # a resposta de usuario e sempre o UserRead (sem senha)


class UserCreate(SQLModel):
    tenant_id: int
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6)
    role: UserRole = UserRole.CLIENTE


class UserUpdate(SQLModel):
    username: str | None = Field(default=None, min_length=3, max_length=50)
    password: str | None = Field(default=None, min_length=6)
    role: UserRole | None = None
    is_active: bool | None = None


__all__ = ["UserCreate", "UserRead", "UserUpdate"]
