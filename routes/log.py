from typing import Annotated

from fastapi import APIRouter, Query

from controller.log import get_logs
from controller.permissions import AdminUser
from schemas.log_schema import LogFilter, LogPage

router = APIRouter(prefix="/logs", tags=["logs"])

# so admin e somente leitura: de proposito nao existe rota para editar ou apagar log,
# assim quem invadir uma conta de admin nao consegue apagar os proprios rastros


@router.get("/", response_model=LogPage)
async def get_all(filters: Annotated[LogFilter, Query()], current_user: AdminUser):
    return await get_logs(filters)
