from typing import Annotated

from fastapi import APIRouter, Query
from sqlalchemy import select
from sqlalchemy.sql import func, distinct
from sqlalchemy.orm import aliased


from app.models.filters import FiltreTemporelStructure
from app.models.db import Marche, Structure, Lieu
from app.models.enums import TypeCodeLieu
from app.models.dto import (
    MarcheDto,
    MarcheProcedureDto,
    MarcheNatureDto,
    IndicateursDto,
    MarcheCcagDto,
    MarcheDepartementDto,
)
from app.dependencies import SessionDep

router = APIRouter()


def application_filtres(stmt, f: FiltreTemporelStructure):
    acheteur = aliased(Structure)
    titulaires = aliased(Structure)

    if f.date_debut:
        stmt = stmt.where(Marche.date_notification >= f.date_debut)

    if f.date_fin:
        stmt = stmt.where(Marche.date_notification <= f.date_fin)

    if f.identifiant_acheteur:
        stmt = stmt.join(acheteur, Marche.acheteur)
        stmt = stmt.where(acheteur.identifiant == f.identifiant_acheteur)
        stmt = stmt.where(acheteur.type_identifiant == f.type_identifiant)

    if f.identifiant_vendeur:
        stmt = stmt.join(titulaires, Marche.titulaires)
        stmt = stmt.where(titulaires.identifiant == f.identifiant_vendeur)
        stmt = stmt.where(titulaires.type_identifiant == f.type_identifiant)

    return stmt


@router.get("/", response_model=list[MarcheDto])
def get_liste_marches(
    session: SessionDep, limit: int = 20, offset: int = 0
) -> list[Marche]:
    return list(session.execute(select(Marche).offset(offset).limit(limit)).scalars())


@router.get("/procedure", response_model=list[MarcheProcedureDto])
def get_marches_par_procedure(
    session: SessionDep, filtres: Annotated[FiltreTemporelStructure, Query()]
) -> list:
    stmt = application_filtres(
        select(
            Marche.procedure,
            func.sum(Marche.montant).label("montant"),
            func.count(Marche.procedure).label("nombre"),
        ),
        filtres,
    ).group_by(Marche.procedure)

    return list(session.execute(stmt).all())


# ToDo: move to PGSQL
# @router.get("/nature", response_model=list[MarcheNatureDto])
# def get_marches_par_nature(
#     session: SessionDep, filtres: Annotated[FiltreTemporelStructure, Query()]
# ) -> list:
#     stmt = application_filtres(
#         select(
#             Marche.nature,
#             func.sum(Marche.montant).label("montant"),
#             func.count(Marche.id).label("nombre"),
#         ),
#         filtres,
#     ).group_by(Marche.nature, func.month(Marche.date_notification))

#     return list(session.execute(stmt).all())


@router.get("/ccag", response_model=list[MarcheCcagDto])
def get_marches_par_ccag(
    session: SessionDep, filtres: Annotated[FiltreTemporelStructure, Query()]
) -> list:
    stmt = application_filtres(
        select(
            Marche.ccag,
            func.sum(Marche.montant).label("montant"),
            func.count(Marche.ccag).label("nombre"),
        ),
        filtres,
    ).group_by(Marche.ccag)

    return list(session.execute(stmt).all())


@router.get("/indicateurs", response_model=IndicateursDto)
def get_indicateurs(
    session: SessionDep, filtres: Annotated[FiltreTemporelStructure, Query()]
) -> IndicateursDto:
    if filtres.date_debut and filtres.date_fin:
        delta = filtres.date_fin - filtres.date_debut
        periode = int(delta.days / 30)
    else:
        periode = None
    nb_contrats = session.execute(
        application_filtres(select(func.count(Marche.id)), filtres)
    ).one()[0]
    montant_total = session.execute(
        application_filtres(select(func.sum(Marche.montant)), filtres)
    ).one()[0]
    nb_acheteurs = session.execute(
        application_filtres(
            select(func.count(distinct(Structure.uid))).join(Marche.acheteur), filtres
        )
    ).one()[0]
    nb_fournisseurs = session.execute(
        application_filtres(
            select(func.count(distinct(Structure.uid))).join(Marche.titulaires), filtres
        )
    ).one()[0]
    nb_sous_traitance = session.execute(
        application_filtres(
            select(func.count(Marche.sous_traitance_declaree)).where(
                Marche.sous_traitance_declaree == True
            ),
            filtres,
        )
    ).one()[0]
    nb_innovant = session.execute(
        application_filtres(
            select(func.count(Marche.marche_innovant)).where(
                Marche.marche_innovant == True
            ),
            filtres,
        )
    ).one()[0]

    return IndicateursDto(
        periode=periode,
        nb_contrats=nb_contrats,
        montant_total=montant_total,
        nb_acheteurs=nb_acheteurs,
        nb_fournisseurs=nb_fournisseurs,
        nb_sous_traitance=nb_sous_traitance,
        nb_innovant=nb_innovant,
    )


@router.get("/departement", response_model=list[MarcheDepartementDto])
def get_marches_par_departement(session: SessionDep) -> list:
    stmt = (
        select(
            Lieu.code,
            func.sum(Marche.montant).label("montant"),
            func.count(Marche.id).label("nombre"),
        )
        .join(Marche.lieu)
        .where(Lieu.type_code == TypeCodeLieu.DEP.db_value)
    ).group_by(Lieu.code)

    return list(session.execute(stmt).all())
