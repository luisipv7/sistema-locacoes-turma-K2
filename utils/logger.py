import asyncio
import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qsl

import jwt
from dotenv import load_dotenv
from fastapi import Request, Response
from pymongo import AsyncMongoClient
from starlette.datastructures import UploadFile

from security import decode_access_token

load_dotenv()

# sem MONGO_URL no .env os logs ficam desligados e a API funciona normal
MONGO_URL = os.getenv("MONGO_URL")
MONGO_DATABASE = os.getenv("MONGO_DATABASE", "rent-all-logs")
MONGO_COLLECTION = "request_logs"

# paginas do swagger nao sao endpoints da API, entao nao entram no log
IGNORED_PATHS = {"/docs", "/docs/oauth2-redirect", "/redoc", "/openapi.json", "/favicon.ico"}

# nunca salvar senha ou token em texto puro no banco de logs
SENSITIVE_WORDS = ("password", "senha", "token", "secret")
SENSITIVE_HEADERS = {"authorization", "cookie"}
MASK = "***"

# bodies maiores que isso sao salvos so com o tamanho
MAX_BODY_BYTES = 100_000

logger = logging.getLogger(__name__)

_client: AsyncMongoClient | None = None
_pending_tasks: set[asyncio.Task] = set()


def connect_mongo() -> None:
    """Abre a conexao com o Mongo. Chame no startup da API."""
    global _client
    if not MONGO_URL:
        logger.warning("MONGO_URL nao configurado: logs de requisicao desativados")
        return
    _client = AsyncMongoClient(MONGO_URL, serverSelectionTimeoutMS=2000, tz_aware=True)


def get_logs_collection():
    """Colecao onde os logs ficam salvos. Retorna None se os logs estiverem desligados."""
    if _client is None:
        return None
    return _client[MONGO_DATABASE][MONGO_COLLECTION]


async def close_mongo() -> None:
    """Espera os logs que ainda estao sendo salvos e fecha a conexao. Chame no shutdown."""
    global _client
    if _pending_tasks:
        await asyncio.wait(_pending_tasks, timeout=5)
    if _client is not None:
        await _client.close()
        _client = None


async def log_requests(request: Request, call_next) -> Response:
    """Middleware: salva no Mongo tudo que chegou na requisicao + status e tempo da resposta."""
    if _client is None or request.url.path in IGNORED_PATHS:
        return await call_next(request)

    start = time.perf_counter()
    # o body fica em cache, entao o endpoint continua conseguindo ler normalmente
    body = await request.body()

    log: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc),
        "method": request.method,
        "path": request.url.path,
        "query_params": _mask(_query_params(request)),
        "headers": _headers(request),
        "body": await _parse_body(request, body),
        "client_ip": request.client.host if request.client else None,
        "user": _user_from_token(request),
    }

    try:
        response = await call_next(request)
    except Exception as exc:
        log["status_code"] = 500
        log["error"] = repr(exc)
        raise
    else:
        log["status_code"] = response.status_code
        return response
    finally:
        # depois que a rota rodou, o FastAPI ja sabe qual rota foi e quais os path params
        route = request.scope.get("route")
        log["route"] = getattr(route, "path", None)
        log["path_params"] = dict(request.path_params)
        log["duration_ms"] = round((time.perf_counter() - start) * 1000, 2)
        _save_in_background(log)


def _save_in_background(log: dict[str, Any]) -> None:
    """Salva sem fazer o cliente esperar o Mongo responder."""
    collection = get_logs_collection()
    if collection is None:
        return
    task = asyncio.create_task(_save(collection, log))
    _pending_tasks.add(task)
    task.add_done_callback(_pending_tasks.discard)


async def _save(collection, log: dict[str, Any]) -> None:
    try:
        await collection.insert_one(log)
    except Exception as exc:
        # se o Mongo cair, a API continua funcionando; so perde o log
        logger.warning("Nao foi possivel salvar o log de %s %s: %s", log["method"], log["path"], exc)


def _query_params(request: Request) -> dict[str, Any]:
    params = {}
    for key in request.query_params.keys():
        values = request.query_params.getlist(key)
        params[key] = values[0] if len(values) == 1 else values
    return params


def _headers(request: Request) -> dict[str, str]:
    return {
        key: MASK if key in SENSITIVE_HEADERS else value
        for key, value in request.headers.items()
    }


async def _parse_body(request: Request, body: bytes) -> Any:
    """Converte o body para algo legivel no Mongo (json, form ou texto)."""
    if not body:
        return None
    if len(body) > MAX_BODY_BYTES:
        return f"<body grande demais: {len(body)} bytes>"

    content_type = request.headers.get("content-type", "")
    try:
        if "application/json" in content_type:
            return _mask(json.loads(body))
        if "application/x-www-form-urlencoded" in content_type:
            return _mask(dict(parse_qsl(body.decode("utf-8"))))
        if "multipart/form-data" in content_type:
            async with request.form() as form:
                return _mask({
                    key: f"<arquivo {value.filename}, {value.size} bytes>" if isinstance(value, UploadFile) else value
                    for key, value in form.multi_items()
                })
        return body.decode("utf-8")
    except Exception:
        return f"<body nao legivel: {len(body)} bytes>"


def _user_from_token(request: Request) -> dict[str, Any] | None:
    """Descobre quem fez a chamada pelo token JWT (sem consultar o banco)."""
    scheme, _, token = request.headers.get("authorization", "").partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    try:
        payload = decode_access_token(token)
    except jwt.PyJWTError:
        return {"username": None, "role": None, "token_valido": False}
    return {"username": payload.get("sub"), "role": payload.get("role"), "token_valido": True}


def _mask(data: Any) -> Any:
    """Troca o valor de campos sensiveis (senha, token...) por ***, inclusive em objetos aninhados."""
    if isinstance(data, dict):
        return {
            key: MASK if any(word in str(key).lower() for word in SENSITIVE_WORDS) else _mask(value)
            for key, value in data.items()
        }
    if isinstance(data, list):
        return [_mask(item) for item in data]
    return data
