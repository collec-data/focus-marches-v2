from fastapi import APIRouter
from sqlalchemy import select

from app.dependencies import SessionDep
from app.models.db import Lieu
from app.models.dto import LieuDto
from app.models.enums import TypeCodeLieu

router = APIRouter()


@router.get("/", response_model=list[LieuDto])
def get_lieux(session: SessionDep, type_lieu: TypeCodeLieu | None = None) -> list[Lieu]:
    stmt = select(Lieu)

    if type_lieu:
        stmt = stmt.where(Lieu.type_code == type_lieu.db_value)

    return list(session.execute(stmt.order_by(Lieu.type_code, Lieu.code)).scalars())
