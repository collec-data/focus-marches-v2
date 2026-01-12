from datetime import date

from fastapi import APIRouter
from sqlalchemy import Row, desc, func, select

from app.dependencies import SessionDep
from app.models.db import DecpMalForme, Erreur, Structure
from app.models.dto import DecpMalFormeDto, StatsErreursDto

router = APIRouter()


@router.get("/", response_model=list[DecpMalFormeDto])
def get_erreurs_import(
    session: SessionDep,
    limit: int | None = 500,
    offset: int | None = None,
    localisation: str | None = None,
    type: str | None = None,
    uid_structure: int | None = None,
    date_debut: date | None = None,
    date_fin: date | None = None,
) -> list[DecpMalForme]:
    stmt = (
        select(DecpMalForme)
        .outerjoin(DecpMalForme.erreurs)
        .outerjoin(DecpMalForme.structure)
    )

    if uid_structure is not None:
        stmt = stmt.where(Structure.uid == uid_structure)

    if localisation:
        stmt = stmt.where(Erreur.localisation == localisation)

    if type:
        stmt = stmt.where(Erreur.type == type)

    if date_debut:
        stmt = stmt.where(DecpMalForme.date_creation >= date_debut)

    if date_fin:
        stmt = stmt.where(DecpMalForme.date_creation <= date_fin)

    stmt = stmt.order_by(DecpMalForme.uid)

    if limit:
        stmt = stmt.limit(limit)

    if offset:
        stmt = stmt.offset(offset)

    return list(session.execute(stmt).scalars())


@router.get("/stats", response_model=list[StatsErreursDto])
def get_stats_erreurs(
    session: SessionDep,
    date_debut: date | None = None,
    date_fin: date | None = None,
    uid_structure: int | None = None,
) -> list[Row[tuple[int, str, str, str]]]:
    stmt = select(
        func.count(Erreur.message).label("nombre"),
        Erreur.message.label("erreur"),
        Erreur.localisation,
        Erreur.type,
    )
    if date_debut or date_fin or uid_structure:
        stmt = stmt.join(Erreur.decp)

    if date_debut:
        stmt = stmt.where(DecpMalForme.date_creation >= date_debut)

    if date_fin:
        stmt = stmt.where(DecpMalForme.date_creation <= date_fin)

    if uid_structure is not None:
        stmt = stmt.join(DecpMalForme.structure).where(Structure.uid == uid_structure)

    stmt = (
        stmt.group_by(Erreur.message)
        .group_by(Erreur.localisation)
        .group_by(Erreur.type)
        .order_by(desc("nombre"), "localisation")
    )
    return list(session.execute(stmt).all()) or []
