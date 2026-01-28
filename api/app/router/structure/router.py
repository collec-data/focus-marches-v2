import logging
from datetime import date
from decimal import Decimal
from typing import Annotated

from api_entreprise.api import ApiEntreprise
from api_entreprise.exceptions import ApiEntrepriseClientError
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import asc, desc, distinct, func, or_, select
from sqlalchemy.orm import aliased

from app.dependencies import ApiEntrepriseDep, SessionDep
from app.models.db import Marche, Structure, StructureInfogreffe
from app.models.dto import (
    StructureDto,
    StructureEtendueDto,
)
from app.models.enums import IdentifiantStructure
from app.router.structure.models import (
    PaginatedStructureAggMarchesDto,
    ParamsAcheteurs,
    ParamsVendeurs,
    StructuresAggChamps,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=list[StructureDto])
def list_structures(
    session: SessionDep,
    nom: str | None = None,
    is_acheteur: bool = False,
    is_vendeur: bool = False,
) -> list[Structure]:
    stmt = select(Structure)

    if is_acheteur is True:
        stmt = stmt.where(Structure.acheteur)

    if is_vendeur is True:
        stmt = stmt.where(Structure.vendeur)

    if nom:
        stmt = stmt.where(
            or_(Structure.nom.contains(nom), Structure.identifiant.contains(nom))
        )

    return list(session.execute(stmt).scalars())


@router.get("/acheteur", response_model=PaginatedStructureAggMarchesDto)
def list_acheteurs(
    session: SessionDep,
    params: Annotated[ParamsAcheteurs, Query()],
) -> dict[str, int | list[dict[str, Decimal | Structure]]]:
    stmt = (
        select(
            Structure,
            func.sum(Marche.montant).label("montant"),
            func.count(Marche.id).label("nb_contrats"),
        )
        .join(Structure.marches_acheteurs)
        .where(Structure.acheteur.is_(True))
    )
    total = (
        select(func.count(distinct(Structure.uid)).label("total"))
        .join(Structure.marches_acheteurs)
        .where(Structure.acheteur.is_(True))
    )

    if params.vendeur_uid:
        titulaires = aliased(Structure)
        stmt = stmt.outerjoin(titulaires, Marche.titulaires).where(
            titulaires.uid == params.vendeur_uid
        )
        total = total.outerjoin(titulaires, Marche.titulaires).where(
            titulaires.uid == params.vendeur_uid
        )

    if params.filtre is not None and params.filtre != "":
        stmt = stmt.where(
            or_(
                Structure.identifiant.contains(params.filtre),
                Structure.nom.contains(params.filtre),
            )
        )
        total = total.where(
            or_(
                Structure.identifiant.contains(params.filtre),
                Structure.nom.contains(params.filtre),
            )
        )

    if params.categorie:
        stmt = stmt.where(Marche.categorie == params.categorie.db_value)
        total = total.where(Marche.categorie == params.categorie.db_value)

    if params.date_debut:
        stmt = stmt.where(Marche.date_notification >= params.date_debut)
        total = total.where(Marche.date_notification >= params.date_debut)

    if params.date_fin:
        stmt = stmt.where(Marche.date_notification <= params.date_fin)
        total = total.where(Marche.date_notification <= params.date_fin)

    stmt = stmt.group_by(Structure.uid)

    if params.champs_ordre == StructuresAggChamps.NOM:
        stmt = stmt.order_by((asc if params.ordre > 0 else desc)(Structure.nom))
    else:
        stmt = stmt.order_by((asc if params.ordre > 0 else desc)(params.champs_ordre))

    stmt = stmt.offset(params.offset)

    if params.limit:
        stmt = stmt.limit(params.limit)

    return {
        "items": [
            {"structure": structure, "montant": montant, "nb_contrats": nb_contrats}
            for structure, montant, nb_contrats in session.execute(stmt).all()
        ],
        "total": session.execute(total).scalar_one(),
    }


@router.get("/vendeur", response_model=PaginatedStructureAggMarchesDto)
def list_vendeurs(
    session: SessionDep,
    params: Annotated[ParamsVendeurs, Query()],
) -> dict[str, int | list[dict[str, Decimal | Structure]]]:
    stmt = (
        select(
            Structure,
            func.sum(Marche.montant).label("montant"),
            func.count(Marche.id).label("nb_contrats"),
        )
        .join(Structure.marches_vendeur)
        .where(Structure.vendeur.is_(True))
    )
    total = (
        select(func.count(distinct(Structure.uid)).label("total"))
        .join(Structure.marches_vendeur)
        .where(Structure.vendeur.is_(True))
    )

    if params.filtre is not None and params.filtre != "":
        stmt = stmt.where(
            or_(
                Structure.identifiant.contains(params.filtre),
                Structure.nom.contains(params.filtre),
            )
        )
        total = total.where(
            or_(
                Structure.identifiant.contains(params.filtre),
                Structure.nom.contains(params.filtre),
            )
        )

    if params.acheteur_uid:
        stmt = stmt.where(Marche.uid_acheteur == params.acheteur_uid)
        total = total.where(Marche.uid_acheteur == params.acheteur_uid)

    if params.categorie:
        stmt = stmt.where(Marche.categorie == params.categorie.db_value)
        total = total.where(Marche.categorie == params.categorie.db_value)

    if params.date_debut:
        stmt = stmt.where(Marche.date_notification >= params.date_debut)
        total = total.where(Marche.date_notification >= params.date_debut)

    if params.date_fin:
        stmt = stmt.where(Marche.date_notification <= params.date_fin)
        total = total.where(Marche.date_notification <= params.date_fin)

    stmt = stmt.group_by(Structure.uid)

    if params.champs_ordre == StructuresAggChamps.NOM:
        stmt = stmt.order_by((asc if params.ordre > 0 else desc)(Structure.nom))
    else:
        stmt = stmt.order_by((asc if params.ordre > 0 else desc)(params.champs_ordre))

    stmt = stmt.offset(params.offset)

    if params.limit:
        stmt = stmt.limit(params.limit)

    return {
        "items": [
            {"structure": structure, "montant": montant, "nb_contrats": nb_contrats}
            for structure, montant, nb_contrats in session.execute(stmt).all()
        ],
        "total": session.execute(total).scalar_one(),
    }


def complete_structure_etendue(
    structure: Structure, api_entreprise: ApiEntreprise
) -> StructureEtendueDto:
    structure_dto = StructureEtendueDto.model_validate(structure, from_attributes=True)

    if structure.type_identifiant == "SIRET":
        try:
            details = api_entreprise.donnees_etablissement(structure.identifiant)
            if details:
                structure_dto.denomination = (
                    details.unite_legale.personne_morale_attributs.raison_sociale
                )
                structure_dto.sigle = (
                    details.unite_legale.personne_morale_attributs.sigle
                )
                structure_dto.adresse = details.adresse_postale_legere
                structure_dto.cat_juridique = details.unite_legale.forme_juridique.code
                structure_dto.naf = details.unite_legale.activite_principale.code
                structure_dto.effectifs = (
                    details.unite_legale.tranche_effectif_salarie.intitule
                )
                structure_dto.date_effectifs = int(
                    details.unite_legale.tranche_effectif_salarie.date_reference or "0"
                )
                structure_dto.date_creation = (
                    date.fromtimestamp(float(details.date_creation))
                    if details.date_creation
                    else None
                )
        except ApiEntrepriseClientError as e:
            logger.error(f"API entreprise - {str(e)}")

    return structure_dto


@router.get("/{uid}", response_model=StructureEtendueDto)
def get_structure(
    uid: int,
    session: SessionDep,
    api_entreprise: ApiEntrepriseDep,
) -> StructureEtendueDto:
    stmt = (
        select(Structure)
        .outerjoin(Structure.infogreffe)
        .where(Structure.uid == uid)
        .order_by(StructureInfogreffe.annee.asc())
    )
    structure = session.execute(stmt).scalar()

    if not structure:
        raise HTTPException(status_code=404, detail="Structure inconnue")

    return complete_structure_etendue(structure, api_entreprise)


@router.get("/{type_id}/{id}", response_model=StructureEtendueDto)
def get_structure_id(
    type_id: IdentifiantStructure,
    id: str,
    session: SessionDep,
    api_entreprise: ApiEntrepriseDep,
) -> StructureEtendueDto:
    stmt = (
        select(Structure)
        .outerjoin(Structure.infogreffe)
        .where(Structure.identifiant == id)
        .where(Structure.type_identifiant == type_id)
        .order_by(StructureInfogreffe.annee.asc())
    )
    structure = session.execute(stmt).scalar()

    if not structure:
        raise HTTPException(status_code=404, detail="Structure inconnue")

    return complete_structure_etendue(structure, api_entreprise)
