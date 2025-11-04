from fastapi import APIRouter
from sqlalchemy import Row, desc, func, select

from app.dependencies import SessionDep
from app.models.db import DecpMalForme, Erreur
from app.models.dto import DecpMalFormeDto, StatsErreursDto

router = APIRouter()


@router.get("/", response_model=list[DecpMalFormeDto])
def get_erreurs_import(
    session: SessionDep,
    limit: int | None = None,
    offset: int | None = None,
    localisation: str | None = None,
    type: str | None = None,
) -> list[DecpMalForme]:
    stmt = select(DecpMalForme).outerjoin(DecpMalForme.erreurs)

    if localisation:
        stmt = stmt.where(Erreur.localisation == localisation)

    if type:
        stmt = stmt.where(Erreur.type == type)

    stmt = stmt.order_by(DecpMalForme.uid)

    if limit:
        stmt = stmt.limit(limit)

    if offset:
        stmt = stmt.offset(offset)

    return list(session.execute(stmt).scalars())


@router.get("/stats", response_model=list[StatsErreursDto])
def get_stats_erreurs(session: SessionDep) -> list[Row[tuple[int, str, str, str]]]:
    stmt = (
        select(
            func.count(Erreur.message).label("nombre"),
            Erreur.message.label("erreur"),
            Erreur.localisation,
            Erreur.type,
        )
        .group_by(Erreur.message)
        .group_by(Erreur.localisation)
        .group_by(Erreur.type)
        .order_by(desc("nombre"), "localisation")
    )
    return list(session.execute(stmt).all()) or []
