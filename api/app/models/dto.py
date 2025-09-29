from decimal import Decimal
from datetime import date
from typing import Optional, Any

from pydantic import BaseModel, Json, Field

from .enums import *


class StructureDto(BaseModel):
    uid: int
    identifiant: str
    type_identifiant: str
    nom: str | None
    vendeur: bool
    acheteur: bool


class StructureEtendueDto(StructureDto):
    denomination: str | None = None
    sigle: str | None = None
    adresse: str | None = None
    cat_juridique: str | None = None
    naf: str | None = None
    effectifs: str | None = None
    date_effectifs: int | None = None


class ActeSousTraitanceDto(BaseModel):
    uid: int
    # id: int
    # sous_traitant: StructureDto
    # duree_mois: int | None
    # date_notification: date
    # date_publication: date
    # montant: Decimal
    # variation_prix: VariationPrix


class ModificationMarcheDto(BaseModel):
    uid: int
    id: int
    duree_mois: int | None
    date_notification: date
    date_publication: date
    montant: Decimal | None
    titulaires: list[StructureDto]


class ModificationSousTraitanceDto(BaseModel):
    uid: int
    uid_acte_sous_traitance: int
    duree_mois: int
    date_notif: date
    date_publication: date
    montant: Decimal


class LieuDto(BaseModel):
    uid: int
    code: str
    type_code: str


class TarifDto(BaseModel):
    uid: int
    uid_donnee_execution: int
    intitule: str
    tarif: Decimal


class DonneeExecutionDto(BaseModel):
    uid: int
    id: int
    uid_contrat_concession: int
    date_publication: date
    depenses_investissement: Decimal
    tarifs: list[TarifDto]


class MarcheAllegeDto(BaseModel):
    uid: int
    id: str
    acheteur: StructureDto
    objet: str
    cpv: str = Field(
        description="Nomenclature européenne permettant d'identifier les catégories de biens et de service faisant l'objet du marché (http://simap.ted.europa.eu/web/simap/cpv). Exemple: 45112500 (même si toléré, il préférable d'omettre le caractère de contrôle (-9))"
    )
    sous_traitance_declaree: bool
    actes_sous_traitance: list[ActeSousTraitanceDto]
    date_notification: date
    montant: Decimal
    titulaires: list[StructureDto]
    # considerations_sociales: list[ConsiderationsSociales]
    # considerations_environnementales: list[ConsiderationsEnvironnementales]


class MarcheDto(BaseModel):
    uid: int
    id: str
    acheteur: StructureDto
    nature: NatureMarche
    objet: str
    cpv: str = Field(
        description="Nomenclature européenne permettant d'identifier les catégories de biens et de service faisant l'objet du marché (http://simap.ted.europa.eu/web/simap/cpv). Exemple: 45112500 (même si toléré, il préférable d'omettre le caractère de contrôle (-9))"
    )
    techniques_achat: list[TechniqueAchat]
    modalites_execution: list[ModaliteExecution]
    accord_cadre: Optional["MarcheDto"]
    marche_innovant: bool
    ccag: int | None = Field(
        description="Cahiers des clauses administratives générales de référence du marché public"
    )
    offres_recues: int = Field(
        description="Nombre d'offres reçues par l'acheteur de la part des soumissionnaires. Comprend aussi les offres irrégulières, inacceptables, inappropriées et anormalement basses."
    )
    attribution_avance: bool = Field(
        description="Une avance a été attribuée au titulaire principal du marché public"
    )
    taux_avance: Decimal = Field(
        description="Taux de l'avance attribuée au titulaire principal du marché public par rapport au montant du marché (O.1 = 10 % du montant du marché). En fonction de la valeur de attributionAvance, une valeur égale à 0 signifie soit qu'aucune avance n'a été accordée (si attributionAvance=false), soit que le taux de l'avance n'est pas connu (si attributionAvance=true)."
    )
    type_groupement_operateurs: TypeGroupementOperateur | None
    sous_traitance_declaree: bool
    actes_sous_traitance: list[ActeSousTraitanceDto]
    # procedure: ProcedureMarche | None
    lieu: LieuDto
    duree_mois: int
    date_notification: date
    date_publication: date | None
    montant: Decimal
    type_prix: list[TypePrix] | None
    forme_prix: FormePrix | None
    origine_ue: Decimal | None
    origine_france: Decimal | None
    titulaires: list[StructureDto]
    considerations_sociales: list[ConsiderationsSociales]
    considerations_environnementales: list[ConsiderationsEnvironnementales]
    # modifications_actes_sous_traitance: list[ModificationSousTraitanceDto]
    modifications: list[ModificationMarcheDto]

    # @field_validator("procedure", mode="before")
    # @classmethod
    # def transform(cls, i: int) -> ProcedureMarche:
    #     return int(x), int(y)


class ModificationConcessionDto(BaseModel):
    uid: int
    id: int
    date_signature: date
    date_publication: date
    duree_mois: int | None
    valeur_globale: Decimal | None


class ContratConcessionDto(BaseModel):
    uid: int
    id: int
    autorite_concedante: StructureDto
    # nature: NatureConcession | None
    objet: str
    # procedure: ProcedureConcession | None
    # duree_mois: int
    # date_signature: date
    # date_publication: date
    # date_debut_execution: date
    # valeur_globale: Decimal
    # montant_subvention_publique: Decimal
    # donnees_execution: list[DonneeExecutionDto]
    # concessionnaires: list[StructureDto]
    # considerations_sociales: list[ConsiderationsSociales]
    # considerations_environnementales: list[ConsiderationsEnvironnementales]
    # modifications: list[ModificationConcessionDto]


class ErreurDto(BaseModel):
    type: str
    localisation: str
    message: str


class DecpMalFormeDto(BaseModel):
    decp: Json[dict[str, Any]]
    erreurs: list[ErreurDto]


class MarcheProcedureDto(BaseModel):
    procedure: int | None
    montant: Decimal
    nombre: int


class MarcheNatureDto(BaseModel):
    mois: date
    nature: int
    montant: Decimal
    nombre: int


class MarcheCcagDto(BaseModel):
    ccag: int | None
    montant: Decimal
    nombre: int


class IndicateursDto(BaseModel):
    periode: int | None
    nb_contrats: int
    montant_total: Decimal | None
    nb_acheteurs: int
    nb_fournisseurs: int
    nb_sous_traitance: int
    nb_innovant: int


class MarcheDepartementDto(BaseModel):
    code: str
    montant: Decimal
    nombre: int


class StructureAggMarchesDto(BaseModel):
    structure: StructureDto
    montant: Decimal
    nb_contrats: int
