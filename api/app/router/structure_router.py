from decimal import Decimal

from fastapi import APIRouter
from sqlalchemy import select, func, desc

from app.models.db import Structure, Marche
from app.models.dto import StructureAggMarchesDto
from app.dependencies import SessionDep


router = APIRouter()


@router.get("/acheteur", response_model=list[StructureAggMarchesDto])
def list_acheteurs(
    session: SessionDep, limit: int | None = None
) -> list[dict[str, Decimal | Structure]]:
    stmt = (
        select(
            Structure,
            func.sum(Marche.montant).label("montant"),
            func.count(Marche.id).label("nb_contrats"),
        )
        .join(Structure.marches_acheteurs)
        .group_by(Structure.uid)
        .where(Structure.acheteur == True)
        .order_by(desc("montant"))
    )

    if limit:
        stmt = stmt.limit(limit)

    return [
        {"structure": structure, "montant": montant, "nb_contrats": nb_contrats}
        for structure, montant, nb_contrats in session.execute(stmt).all()
    ]


@router.get("/vendeur", response_model=list[StructureAggMarchesDto])
def list_vendeurs(session: SessionDep, limit: int | None = None):
    stmt = (
        select(
            Structure,
            func.sum(Marche.montant).label("montant"),
            func.count(Marche.id).label("nb_contrats"),
        )
        .join(Structure.marches_vendeur)
        .group_by(Structure.uid)
        .where(Structure.vendeur == True)
        .order_by(desc("montant"))
    )

    if limit:
        stmt = stmt.limit(limit)

    return [
        {"structure": structure, "montant": montant, "nb_contrats": nb_contrats}
        for structure, montant, nb_contrats in session.execute(stmt)
    ]
