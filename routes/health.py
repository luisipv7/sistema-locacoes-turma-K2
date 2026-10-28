from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import literal
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, select

from database import get_session


router = APIRouter(prefix="/health-check", tags=["health"])

@router.get("/")
def health_check(session: Annotated[Session, Depends(get_session)]):
    try:
        result = session.exec(select(literal(1))).one()
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Banco de dados indisponível",
        ) from exc

    if result != 1:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Resposta inesperada do banco de dados",
        )

    return "Conexão estabelecida com sucesso 200 OK"
