from typing import Annotated

from fastapi import APIRouter, Depends


router = APIRouter(prefix="/health-check", tags=["health"])

@router.get("/")
def health_check():
    return "Conexão estabelecida com sucesso 200 OK"