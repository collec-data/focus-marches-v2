from datetime import date
from decimal import Decimal

from fastapi import APIRouter, HTTPException
from sqlalchemy import desc, func, select
from sqlalchemy.orm import aliased

from app.dependencies import ApiEntrepriseDep, SessionDep
from app.models.db import Marche, Structure
from app.models.dto import StructureAggMarchesDto, StructureDto, StructureEtendueDto
from app.models.enums import CategorieMarche

router = APIRouter()


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
        stmt = stmt.where(Structure.nom.contains(nom))

    return list(session.execute(stmt).scalars())


@router.get("/acheteur", response_model=list[StructureAggMarchesDto])
def list_acheteurs(
    session: SessionDep,
    limit: int | None = None,
    date_debut: date | None = None,
    date_fin: date | None = None,
    vendeur_uid: int | None = None,
    categorie: CategorieMarche | None = None,
) -> list[dict[str, Decimal | Structure]]:
    stmt = (
        select(
            Structure,
            func.sum(Marche.montant).label("montant"),
            func.count(Marche.id).label("nb_contrats"),
        )
        .join(Structure.marches_acheteurs)
        .where(Structure.acheteur.is_(True))
    )

    if vendeur_uid:
        titulaires = aliased(Structure)
        stmt = stmt.outerjoin(titulaires, Marche.titulaires).where(
            titulaires.uid == vendeur_uid
        )

    if categorie:
        stmt = stmt.where(Marche.categorie == categorie.db_value)

    if date_debut:
        stmt = stmt.where(Marche.date_notification >= date_debut)

    if date_fin:
        stmt = stmt.where(Marche.date_notification <= date_fin)

    stmt = stmt.group_by(Structure.uid).order_by(desc("montant"))

    if limit:
        stmt = stmt.limit(limit)

    return [
        {"structure": structure, "montant": montant, "nb_contrats": nb_contrats}
        for structure, montant, nb_contrats in session.execute(stmt).all()
    ]


@router.get("/vendeur", response_model=list[StructureAggMarchesDto])
def list_vendeurs(
    session: SessionDep,
    limit: int | None = None,
    acheteur_uid: int | None = None,
    date_debut: date | None = None,
    date_fin: date | None = None,
    categorie: CategorieMarche | None = None,
) -> list[dict[str, Structure | Decimal | int]]:
    stmt = (
        select(
            Structure,
            func.sum(Marche.montant).label("montant"),
            func.count(Marche.id).label("nb_contrats"),
        )
        .join(Structure.marches_vendeur)
        .where(Structure.vendeur.is_(True))
    )
    if acheteur_uid:
        stmt = stmt.where(Marche.uid_acheteur == acheteur_uid)

    if categorie:
        stmt = stmt.where(Marche.categorie == categorie.db_value)

    if date_debut:
        stmt = stmt.where(Marche.date_notification >= date_debut)

    if date_fin:
        stmt = stmt.where(Marche.date_notification <= date_fin)

    stmt = stmt.group_by(Structure.uid).order_by(desc("montant"))

    if limit:
        stmt = stmt.limit(limit)

    return [
        {"structure": structure, "montant": montant, "nb_contrats": nb_contrats}
        for structure, montant, nb_contrats in session.execute(stmt)
    ]


@router.get("/{uid}", response_model=StructureEtendueDto)
def get_structure(
    uid: int,
    session: SessionDep,
    api_entreprise: ApiEntrepriseDep,
) -> StructureEtendueDto:
    stmt = select(Structure).where(Structure.uid == uid)
    structure = session.execute(stmt).scalar()

    if not structure:
        raise HTTPException(status_code=404, detail="Structure inconnue")

    structure_dto = StructureEtendueDto.model_validate(structure.__dict__)

    if structure.type_identifiant == "SIRET":
        details = api_entreprise.donnees_etablissement(structure.identifiant)
        if details:
            structure_dto.denomination = (
                details.unite_legale.personne_morale_attributs.raison_sociale
            )
            structure_dto.sigle = details.unite_legale.personne_morale_attributs.sigle
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

    return structure_dto
