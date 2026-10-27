# /schemas/user_schema.py

from sqlmodel import SQLModel

from models.enums import UserRole


class UserCreate(SQLModel):
    tenant_id: int
    username: str
    password: str
    role: UserRole = UserRole.CLIENTE


class UserRead(SQLModel):
    id: int
    tenant_id: int
    username: str
    role: UserRole
    is_active: bool


class UserUpdate(SQLModel):
    username: str | None = None
    password: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None