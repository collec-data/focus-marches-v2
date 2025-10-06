from fastapi import APIRouter
from sqlalchemy import select

from app.dependencies import SessionDep
from app.models.db import DecpMalForme
from app.models.dto import DecpMalFormeDto

router = APIRouter()


@router.get("/", response_model=list[DecpMalFormeDto])
def get_erreurs_import(
    session: SessionDep, limit: int = 50, offset: int = 0
) -> list[DecpMalForme]:
    return list(
        session.execute(
            select(DecpMalForme).order_by(DecpMalForme.uid).limit(limit).offset(offset)
        ).scalars()
    )
