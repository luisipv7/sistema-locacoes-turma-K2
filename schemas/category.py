from sqlmodel import SQLModel


class CategoryCreate(SQLModel):
    tenant_id: int
    name: str
    slug: str
    description: str | None = None
    parent_id: int | None = None


class CategoryRead(SQLModel):
    id: int
    tenant_id: int
    name: str
    slug: str
    description: str | None
    parent_id: int | None


class CategoryUpdate(SQLModel):
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    parent_id: int | None = None