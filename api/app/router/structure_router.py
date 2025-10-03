from decimal import Decimal

from fastapi import APIRouter, HTTPException
from sqlalchemy import desc, func, select

from app.dependencies import ApiEntrepriseDep, SessionDep
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
    uid: int, session: SessionDep, api_entreprise: ApiEntrepriseDep
) -> Structure:
    stmt = select(Structure).where(Structure.uid == uid)
    structure = session.execute(stmt).scalar()

    if not structure:
        raise HTTPException(status_code=404, detail="Structure inconnue")

    if structure.type_identifiant == "SIRET":
        details = api_entreprise.donnees_etablissement(structure.identifiant)
        if details:
            dict_structure = structure.__dict__
            dict_structure["denomination"] = (
                details.unite_legale.personne_morale_attributs.raison_sociale
            )
            dict_structure["sigle"] = (
                details.unite_legale.personne_morale_attributs.sigle
            )
            dict_structure["adresse"] = details.adresse_postale_legere
            dict_structure["cat_juridique"] = details.unite_legale.forme_juridique.code
            dict_structure["naf"] = details.unite_legale.activite_principale.code
            dict_structure["effectifs"] = (
                details.unite_legale.tranche_effectif_salarie.intitule
            )
            dict_structure["date_effectifs"] = (
                details.unite_legale.tranche_effectif_salarie.date_reference
            )

    return structure
