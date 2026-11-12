# /schemas/log_schema.py

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class LogFilter(BaseModel):
    """Filtros do GET /logs. Todos sao opcionais e podem ser combinados."""

    skip: int = Field(0, ge=0)
    limit: int = Field(50, ge=1, le=100)
    username: str | None = None
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"] | None = None
    path: str | None = Field(None, description="Busca parcial: /users encontra /users/1")
    status_code: int | None = Field(None, ge=100, le=599)
    start: datetime | None = Field(None, description="A partir de. Sem fuso e UTC. Ex: 2026-11-12T10:00:00-03:00")
    end: datetime | None = Field(None, description="Ate. Sem fuso e UTC. Ex: 2026-11-12T18:00:00-03:00")


class LogUser(BaseModel):
    username: str | None = None
    role: str | None = None
    token_valido: bool


class LogRead(BaseModel):
    id: str
    timestamp: datetime
    method: str
    path: str
    route: str | None = None
    path_params: dict[str, Any] = {}
    query_params: dict[str, Any] = {}
    headers: dict[str, str] = {}
    body: Any = None
    client_ip: str | None = None
    user: LogUser | None = None
    status_code: int | None = None
    duration_ms: float | None = None
    error: str | None = None


class LogPage(BaseModel):
    total: int
    skip: int
    limit: int
    items: list[LogRead]
