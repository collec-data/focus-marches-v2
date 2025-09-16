from decimal import Decimal

from fastapi import APIRouter
from sqlalchemy import select, func

from app.models.db import Structure, Marche
from app.models.dto import AcheteurDto
from app.dependencies import SessionDep


router = APIRouter()


@router.get("/acheteur", response_model=list[AcheteurDto])
def list_acheteurs(session: SessionDep) -> list[dict[str, Decimal | Structure]]:
    return [
        {"structure": structure, "montant": montant}
        for structure, montant in session.execute(
            select(Structure, func.sum(Marche.montant))
            .join(Structure.marches_acheteurs)
            .group_by(Structure.identifiant)
            .where(Structure.acheteur == True)
        ).all()
    ]
