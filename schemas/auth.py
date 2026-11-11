from sqlmodel import Field, SQLModel
from models.enums import UserRole

class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(SQLModel):
    username: str | None = None


class UserRead(SQLModel):
    id: int
    tenant_id: int | None
    username: str
    role: str
    is_active: bool

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
