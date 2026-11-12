import re
from typing import Any

from fastapi import HTTPException, status
from pymongo import DESCENDING
from pymongo.errors import PyMongoError

from schemas.log_schema import LogFilter
from utils.logger import get_logs_collection


def _build_query(filters: LogFilter) -> dict[str, Any]:
    """Monta o filtro do Mongo so com os campos que foram informados."""
    query: dict[str, Any] = {}
    if filters.username:
        query["user.username"] = filters.username
    if filters.method:
        query["method"] = filters.method
    if filters.path:
        # re.escape: o texto digitado e buscado literalmente, nunca como expressao regular
        query["path"] = {"$regex": re.escape(filters.path), "$options": "i"}
    if filters.status_code is not None:
        query["status_code"] = filters.status_code
    if filters.start or filters.end:
        query["timestamp"] = {}
        if filters.start:
            query["timestamp"]["$gte"] = filters.start
        if filters.end:
            query["timestamp"]["$lte"] = filters.end
    return query


async def get_logs_service(filters: LogFilter) -> dict[str, Any]:
    collection = get_logs_collection()
    if collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Logs desativados: configure o MONGO_URL no .env",
        )

    query = _build_query(filters)
    try:
        total = await collection.count_documents(query)
        cursor = (
            collection.find(query)
            .sort("timestamp", DESCENDING)  # mais recentes primeiro
            .skip(filters.skip)
            .limit(filters.limit)
        )
        logs = await cursor.to_list()
    except PyMongoError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Banco de logs indisponivel",
        ) from exc

    for log in logs:
        log["id"] = str(log.pop("_id"))

    return {"total": total, "skip": filters.skip, "limit": filters.limit, "items": logs}
