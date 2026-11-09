from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.dependencies import SessionDep
from app.models.db import ContratConcession, DonneeExecution, Structure
from app.models.dto import ContratConcessionDto
from app.models.filters import FiltreListesConcessions

router = APIRouter()


@router.get("/", response_model=list[ContratConcessionDto])
def get_liste_concessions(
    session: SessionDep, filtres: Annotated[FiltreListesConcessions, Query()]
) -> list[ContratConcession]:
    stmt = select(ContratConcession).options(
        selectinload(ContratConcession.autorite_concedante),
        selectinload(ContratConcession.concessionnaires),
        selectinload(ContratConcession.donnees_execution).selectinload(
            DonneeExecution.tarifs
        ),
    )

    if filtres.date_debut:
        stmt = stmt.where(ContratConcession.date_publication >= filtres.date_debut)

    if filtres.date_fin:
        stmt = stmt.where(ContratConcession.date_publication <= filtres.date_fin)

    if filtres.autorite_concedante_uid:
        stmt = stmt.where(
            ContratConcession.autorite_concedante.has(
                Structure.uid == int(filtres.autorite_concedante_uid)
            )
        )

    if filtres.concessionnaire_uid:
        stmt = stmt.where(
            ContratConcession.concessionnaires.any(
                Structure.uid == int(filtres.concessionnaire_uid)
            )
        )

    if filtres.limit:
        stmt = stmt.limit(filtres.limit)

    if filtres.offset:
        stmt = stmt.offset(filtres.offset)

    return list(session.execute(stmt).scalars())


@router.get("/{uid}", response_model=ContratConcessionDto)
def get_concession(uid: int, session: SessionDep) -> ContratConcession:
    stmt = select(ContratConcession).where(ContratConcession.uid == uid)
    concession = session.execute(stmt).scalar()

    if not concession:
        raise HTTPException(status_code=404, detail="Concession inconnue")

    return concession
