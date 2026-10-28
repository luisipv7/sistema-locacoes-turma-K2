from typing import Annotated
from fastapi import APIRouter, Depends
from sqlmodel import Session
from database import get_session
from controller.item import ItemService


router = APIRouter(prefix="/items", tags=["items"])


@router.get("/")
async def get_all(session: Session = Depends(get_session), skip: int = 0, limit: int | None = None, ):
    return await ItemService.get_all_items(session, skip, limit)
