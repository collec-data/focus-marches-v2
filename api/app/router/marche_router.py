from decimal import Decimal
from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import Row, Select, asc, desc, distinct, func, select
from sqlalchemy.orm import aliased

from app.dependencies import SessionDep
from app.models.db import (
    ConsiderationEnvMarche,
    ConsiderationSocialeMarche,
    Lieu,
    Marche,
    Structure,
    TechniqueAchatMarche,
)
from app.models.dto import (
    CategoriesDto,
    IndicateursDto,
    MarcheAllegeDto,
    MarcheCategorieDepartementDto,
    MarcheCcagDto,
    MarcheDepartementDto,
    MarcheDto,
    MarcheNatureDto,
    MarcheProcedureDto,
)
from app.models.enums import (
    ConsiderationsEnvironnementales,
    ConsiderationsSociales,
    TypeCodeLieu,
)
from app.models.filters import (
    FiltreMarchesEtendus,
    FiltresListeMarches,
    FiltreTemporelStructure,
)

router = APIRouter()


def application_filtres(stmt: Select[Any], f: FiltreTemporelStructure) -> Select[Any]:
    acheteur = aliased(Structure)
    titulaires = aliased(Structure)

    if f.date_debut:
        stmt = stmt.where(Marche.date_notification >= f.date_debut)

    if f.date_fin:
        stmt = stmt.where(Marche.date_notification <= f.date_fin)

    if f.acheteur_uid:
        stmt = stmt.join(acheteur, Marche.acheteur)
        stmt = stmt.where(acheteur.uid == int(f.acheteur_uid))

    if f.vendeur_uid:
        stmt = stmt.join(titulaires, Marche.titulaires)
        stmt = stmt.where(titulaires.uid == int(f.vendeur_uid))

    return stmt


def application_filtres_etendus(
    stmt: Select[Any], f: FiltreMarchesEtendus
) -> Select[Any]:
    stmt = application_filtres(stmt=stmt, f=f)

    if f.objet:
        stmt = stmt.where(Marche.objet.contains(f.objet))

    if f.cpv:
        stmt = stmt.where(Marche.cpv.startswith(f.cpv))

    if f.code_lieu:
        stmt = (
            stmt.join(Marche.lieu)
            .where(Lieu.code == str(f.code_lieu))
            .where(Lieu.type_code == TypeCodeLieu.DEP.db_value)
        )

    if f.forme_prix:
        stmt = stmt.where(Marche.forme_prix == f.forme_prix.db_value)

    if f.type_marche:
        stmt = stmt.where(Marche.nature == f.type_marche.db_value)

    if f.procedure:
        stmt = stmt.where(Marche.procedure == f.procedure.db_value)

    if f.categorie:
        stmt = stmt.where(Marche.categorie == f.categorie.db_value)

    if f.technique_achat:
        stmt = stmt.join(Marche.techniques_achat).where(
            TechniqueAchatMarche.technique == f.technique_achat.db_value
        )

    if f.consideration and isinstance(f.consideration, ConsiderationsEnvironnementales):
        stmt = stmt.join(Marche.considerations_environnementales).where(
            ConsiderationEnvMarche.consideration == f.consideration.db_value
        )

    if f.consideration and isinstance(f.consideration, ConsiderationsSociales):
        stmt = stmt.join(Marche.considerations_sociales).where(
            ConsiderationSocialeMarche.consideration == f.consideration.db_value
        )

    if f.montant_max:
        stmt = stmt.where(Marche.montant <= f.montant_max)

    if f.montant_min:
        stmt = stmt.where(Marche.montant >= f.montant_min)

    if f.duree_max:
        stmt = stmt.where(Marche.duree_mois <= f.duree_max)

    if f.duree_min:
        stmt = stmt.where(Marche.duree_mois >= f.duree_min)

    return stmt


@router.get("/", response_model=list[MarcheAllegeDto])
def get_liste_marches(
    session: SessionDep,
    filtres: Annotated[FiltresListeMarches, Query()],
) -> list[Marche]:
    acheteur = aliased(Structure)
    titulaires = aliased(Structure)

    stmt = application_filtres_etendus(
        select(Marche)
        .join(acheteur, Marche.acheteur, isouter=True)
        .join(titulaires, Marche.titulaires, isouter=True)
        .join(Marche.actes_sous_traitance, isouter=True),
        filtres,
    ).order_by(Marche.date_notification)

    if filtres.offset is not None:
        stmt = stmt.offset(filtres.offset)

    if filtres.limit is not None:
        stmt = stmt.limit(filtres.limit)

    return list(session.execute(stmt).scalars())


@router.get("/procedure", response_model=list[MarcheProcedureDto])
def get_marches_par_procedure(
    session: SessionDep, filtres: Annotated[FiltreTemporelStructure, Query()]
) -> list[Row[tuple[int | None, Decimal, int]]]:
    stmt = (
        application_filtres(
            select(
                Marche.procedure,
                func.sum(Marche.montant).label("montant"),
                func.count(Marche.procedure).label("nombre"),
            ),
            filtres,
        )
        .group_by(Marche.procedure)
        .order_by(Marche.procedure)
    )

    return list(session.execute(stmt).all())


@router.get("/nature", response_model=list[MarcheNatureDto])
def get_marches_par_nature(
    session: SessionDep, filtres: Annotated[FiltreTemporelStructure, Query()]
) -> list[Row[tuple[int | None, Decimal, int]]]:
    stmt = (
        application_filtres(
            select(
                Marche.nature,
                func.to_char(Marche.date_notification, "YYYY-MM").label("mois"),
                func.sum(Marche.montant).label("montant"),
                func.count(Marche.uid).label("nombre"),
            ),
            filtres,
        )
        .group_by(Marche.nature, "mois")
        .order_by(Marche.nature, "mois")
    )
    return list(session.execute(stmt).all())


@router.get("/ccag", response_model=list[MarcheCcagDto])
def get_marches_par_ccag(
    session: SessionDep, filtres: Annotated[FiltreTemporelStructure, Query()]
) -> list[Row[tuple[int | None, Decimal, int]]]:
    stmt = (
        application_filtres(
            select(
                Marche.ccag,
                Marche.categorie,
                func.sum(Marche.montant).label("montant"),
                func.count(Marche.ccag).label("nombre"),
            ),
            filtres,
        )
        .group_by(Marche.ccag)
        .group_by(Marche.categorie)
        .order_by(desc("montant"))
    )

    return list(session.execute(stmt).all())


@router.get("/indicateurs", response_model=IndicateursDto)
def get_indicateurs(
    session: SessionDep, filtres: Annotated[FiltreMarchesEtendus, Query()]
) -> IndicateursDto:
    if filtres.date_debut and filtres.date_fin:
        delta = filtres.date_fin - filtres.date_debut
        periode = int(delta.days / 30)
    else:
        periode = None
    nb_contrats = session.execute(
        application_filtres_etendus(select(func.count(Marche.id)), filtres)
    ).scalar()
    montant_total = session.execute(
        application_filtres_etendus(select(func.sum(Marche.montant)), filtres)
    ).scalar()
    nb_acheteurs = session.execute(
        application_filtres_etendus(
            select(func.count(distinct(Structure.uid))).join(Marche.acheteur), filtres
        )
    ).scalar()
    nb_fournisseurs = session.execute(
        application_filtres_etendus(
            select(func.count(distinct(Structure.uid))).join(Marche.titulaires), filtres
        )
    ).scalar()
    nb_sous_traitance = session.execute(
        application_filtres_etendus(
            select(func.count(Marche.sous_traitance_declaree)).where(
                Marche.sous_traitance_declaree.is_(True)
            ),
            filtres,
        )
    ).scalar()
    nb_considerations_sociale_env = session.execute(
        application_filtres_etendus(
            select(func.count(Marche.uid))
            .join(Marche.considerations_environnementales)
            .join(Marche.considerations_sociales),
            filtres,
        )
    ).scalar()
    nb_considerations_env = session.execute(
        application_filtres_etendus(
            select(func.count(Marche.uid)).join(
                Marche.considerations_environnementales
            ),
            filtres,
        )
    ).scalar()
    nb_considerations_sociales = session.execute(
        application_filtres_etendus(
            select(func.count(Marche.uid)).join(Marche.considerations_sociales),
            filtres,
        )
    ).scalar()
    nb_innovant = session.execute(
        application_filtres_etendus(
            select(func.count(Marche.marche_innovant)).where(
                Marche.marche_innovant.is_(True)
            ),
            filtres,
        )
    ).scalar()

    return IndicateursDto(
        periode=periode,
        nb_contrats=nb_contrats if nb_contrats else 0,
        montant_total=montant_total if montant_total else Decimal("0"),
        nb_acheteurs=nb_acheteurs if nb_acheteurs else 0,
        nb_fournisseurs=nb_fournisseurs if nb_fournisseurs else 0,
        nb_sous_traitance=nb_sous_traitance if nb_sous_traitance else 0,
        nb_considerations_sociale_env=nb_considerations_sociale_env
        if nb_considerations_sociale_env
        else 0,
        nb_considerations_env=nb_considerations_env if nb_considerations_env else 0,
        nb_considerations_sociales=nb_considerations_sociales
        if nb_considerations_sociales
        else 0,
        nb_innovant=nb_innovant if nb_innovant else 0,
    )


@router.get("/departement", response_model=list[MarcheDepartementDto])
def get_marches_par_departement(
    session: SessionDep,
) -> list[Row[tuple[str, Decimal, int]]]:
    stmt = (
        (
            select(
                func.substr(Lieu.code, 1, 2).label("subcode"),
                func.sum(Marche.montant).label("montant"),
                func.count(Marche.id).label("nombre"),
            )
            .join(Marche.lieu)
            .where(
                Lieu.type_code.in_(
                    [TypeCodeLieu.DEP.db_value, TypeCodeLieu.POSTAL.db_value]
                )
            )
        )
        .group_by("subcode")
        .order_by(asc("montant"))
    )

    return list(session.execute(stmt).all())


@router.get(
    "/categorie-departement", response_model=list[MarcheCategorieDepartementDto]
)
def get_categorie_departement(
    session: SessionDep,
) -> list[Row[tuple[str, int, Decimal]]]:
    stmt = (
        (
            select(
                func.substr(Lieu.code, 1, 2).label("subcode"),
                Marche.categorie,
                func.sum(Marche.montant).label("montant"),
            )
            .join(Marche.lieu)
            .where(
                Lieu.type_code.in_(
                    [TypeCodeLieu.DEP.db_value, TypeCodeLieu.POSTAL.db_value]
                )
            )
        )
        .group_by(Marche.categorie)
        .group_by("subcode")
        .order_by("montant")
    )
    return list(session.execute(stmt).all())


@router.get("/categorie", response_model=list[CategoriesDto])
def get_categories(
    session: SessionDep, filtres: Annotated[FiltreTemporelStructure, Query()]
) -> list[Row[tuple[str]]]:
    stmt = (
        application_filtres(
            select(
                Marche.categorie,
                func.sum(Marche.montant).label("montant"),
                func.count(Marche.id).label("nombre"),
                func.to_char(Marche.date_notification, "YYYY-MM").label("mois"),
            ),
            filtres,
        )
        .group_by(Marche.categorie)
        .group_by("mois")
        .order_by("mois")
    )

    return list(session.execute(stmt).all())


@router.get("/{uid}", response_model=MarcheDto)
def get_marche(uid: int, session: SessionDep) -> Marche:
    stmt = select(Marche).where(Marche.uid == uid)
    marche = session.execute(stmt).scalar()

    if not marche:
        raise HTTPException(status_code=404, detail="Marche inconnu")

    return marche
