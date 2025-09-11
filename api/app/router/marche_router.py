from fastapi import APIRouter
from sqlalchemy import select


from ..models.db import Marche
from ..models.dto import MarcheDto
from ..dependencies import SessionDep

router = APIRouter()


@router.get("/", response_model=list[MarcheDto])
def get_liste_marches(
    session: SessionDep, limit: int = 20, offset: int = 0
) -> list[Marche]:
    return list(session.execute(select(Marche).offset(offset).limit(limit)).scalars())
