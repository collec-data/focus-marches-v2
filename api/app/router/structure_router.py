from decimal import Decimal

from fastapi import APIRouter, HTTPException
from sqlalchemy import desc, func, select

from app.dependencies import ApiEntrepriseDep, OpenDataSoftDep, SessionDep
from app.models.db import Marche, Structure
from app.models.dto import StructureAggMarchesDto, StructureEtendueDto

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
        .where(Structure.acheteur.is_(True))
        .order_by(desc("montant"))
    )

    if limit:
        stmt = stmt.limit(limit)

    return [
        {"structure": structure, "montant": montant, "nb_contrats": nb_contrats}
        for structure, montant, nb_contrats in session.execute(stmt).all()
    ]


@router.get("/vendeur", response_model=list[StructureAggMarchesDto])
def list_vendeurs(
    session: SessionDep, limit: int | None = None
) -> list[dict[str, Structure | Decimal | int]]:
    stmt = (
        select(
            Structure,
            func.sum(Marche.montant).label("montant"),
            func.count(Marche.id).label("nb_contrats"),
        )
        .join(Structure.marches_vendeur)
        .group_by(Structure.uid)
        .where(Structure.vendeur.is_(True))
        .order_by(desc("montant"))
    )

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
    opendatasoft: OpenDataSoftDep,
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
            geoloc = opendatasoft.getCoordonnees(structure.identifiant)
            structure_dto.lon = geoloc["lon"]
            structure_dto.lat = geoloc["lat"]

    return structure_dto
