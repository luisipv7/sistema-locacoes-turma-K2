from typing import Annotated
from fastapi import APIRouter, Depends
from sqlmodel import Session
from controller.category import create_category
from database import get_session
from schemas.category import CategoryCreate
from models.category import Category

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/")
async def create_task(categoria: CategoryCreate, session: Session = Depends(get_session)) -> Category:
    return await  create_category(session, categoria)