from fastapi import APIRouter
from sqlalchemy import select


from app.models.db import ContratConcession
from app.models.dto import ContratConcessionDto
from app.dependencies import SessionDep

router = APIRouter()


@router.get("/", response_model=list[ContratConcessionDto])
def get_liste_concessions(
    session: SessionDep, limit: int = 20, offset: int = 0
) -> list[ContratConcession]:
    return list(
        session.execute(select(ContratConcession).offset(offset).limit(limit)).scalars()
    )
