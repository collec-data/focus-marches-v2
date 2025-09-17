from decimal import Decimal

from fastapi import APIRouter
from sqlalchemy import select, func, desc

from app.models.db import Structure, Marche
from app.models.dto import AcheteurDto
from app.dependencies import SessionDep


router = APIRouter()


@router.get("/acheteur", response_model=list[AcheteurDto])
def list_acheteurs(
    session: SessionDep, limit: int = 12
) -> list[dict[str, Decimal | Structure]]:
    return [
        {"structure": structure, "montant": montant, "nb_contrats": nb_contrats}
        for structure, montant, nb_contrats in session.execute(
            select(
                Structure,
                func.sum(Marche.montant).label("montant"),
                func.count(Marche.id).label("nb_contrats"),
            )
            .join(Structure.marches_acheteurs)
            .group_by(Structure.identifiant)
            .where(Structure.acheteur == True)
            .order_by(desc("montant"))
            .limit(limit)
        ).all()
    ]
