from fastapi import APIRouter
from sqlalchemy import select

from app.dependencies import SessionDep
from app.models.db import CPV
from app.models.dto import CPVDto

router = APIRouter()


@router.get("/", response_model=list[CPVDto])
def list_cpv(session: SessionDep, libelle: str | None = None) -> list[CPV]:
    stmt = select(CPV)

    if libelle:
        stmt = stmt.where(CPV.libelle.contains(libelle))

    stmt = stmt.order_by(CPV.libelle)

    return list(session.execute(stmt).scalars())
