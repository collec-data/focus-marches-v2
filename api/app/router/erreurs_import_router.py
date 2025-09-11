from fastapi import APIRouter
from sqlalchemy import select


from ..models.db import DecpMalForme
from ..models.dto import DecpMalFormeDto
from ..dependencies import SessionDep

router = APIRouter()


@router.get("/", response_model=list[DecpMalFormeDto])
def get_erreurs_import(session: SessionDep) -> list[DecpMalForme]:
    return list(session.execute(select(DecpMalForme)).scalars())
