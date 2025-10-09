from fastapi import APIRouter
from sqlalchemy import Row, desc, func, select

from app.dependencies import SessionDep
from app.models.db import DecpMalForme, Erreur
from app.models.dto import DecpMalFormeDto, StatsErreursDto

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


@router.get("/stats", response_model=list[StatsErreursDto])
def get_stats_erreurs(session: SessionDep) -> list[Row[tuple[int, str, str]]]:
    stmt = (
        select(
            func.count(Erreur.message).label("nombre"),
            Erreur.message.label("erreur"),
            Erreur.localisation,
        )
        .group_by(Erreur.message)
        .group_by(Erreur.localisation)
        .order_by(desc("nombre"), "localisation")
    )
    return list(session.execute(stmt).all()) or []
