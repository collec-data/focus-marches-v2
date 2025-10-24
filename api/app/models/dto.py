from datetime import date
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field, Json, field_validator

from app.models.enums import (
    CCAG,
    CategorieMarche,
    ConsiderationsEnvironnementales,
    ConsiderationsSociales,
    FormePrix,
    ModaliteExecution,
    NatureMarche,
    ProcedureMarche,
    TechniqueAchat,
    TypeCodeLieu,
    TypeGroupementOperateur,
    TypePrix,
    VariationPrix,
)


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
    lon: float | None = None
    lat: float | None = None
    date_creation: date | None = None


class ActeSousTraitanceDto(BaseModel):
    uid: int
    id: int
    sous_traitant: StructureDto
    duree_mois: int | None
    date_notification: date
    date_publication: date
    montant: Decimal
    variation_prix_as_str: VariationPrix = Field(serialization_alias="variation_prix")


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
    type_code_as_str: TypeCodeLieu = Field(serialization_alias="type_code")


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
    categorie_as_str: CategorieMarche = Field(serialization_alias="categorie")
    sous_traitance_declaree: bool
    actes_sous_traitance: list[ActeSousTraitanceDto]
    date_notification: date
    montant: Decimal
    titulaires: list[StructureDto]
    considerations_sociales_as_str: list[ConsiderationsSociales] = Field(
        serialization_alias="considerations_sociales"
    )
    considerations_environnementales_as_str: list[ConsiderationsEnvironnementales] = (
        Field(serialization_alias="considerations_environnementales")
    )


class MarcheDto(BaseModel):
    uid: int
    id: str
    acheteur: StructureDto
    nature_as_str: NatureMarche = Field(serialization_alias="nature")
    objet: str
    cpv: str = Field(
        description="Nomenclature européenne permettant d'identifier les catégories de biens et de service faisant l'objet du marché (http://simap.ted.europa.eu/web/simap/cpv). Exemple: 45112500 (même si toléré, il préférable d'omettre le caractère de contrôle (-9))"
    )
    categorie_as_str: CategorieMarche = Field(serialization_alias="categorie")
    techniques_achat_as_str: list[TechniqueAchat] = Field(
        serialization_alias="techniques_achat"
    )
    modalites_execution_as_str: list[ModaliteExecution] = Field(
        serialization_alias="modalites_execution"
    )
    accord_cadre: "MarcheDto | None"
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
    type_groupement_operateurs_as_str: TypeGroupementOperateur | None = Field(
        serialization_alias="type_groupement_operateurs"
    )
    sous_traitance_declaree: bool
    actes_sous_traitance: list[ActeSousTraitanceDto]
    procedure_as_str: ProcedureMarche | None = Field(serialization_alias="procedure")
    lieu: LieuDto
    duree_mois: int
    date_notification: date
    date_publication: date | None
    montant: Decimal
    type_prix_as_str: list[TypePrix] | None = Field(serialization_alias="type_prix")
    forme_prix_as_str: FormePrix | None = Field(serialization_alias="forme_prix")
    origine_ue: Decimal | None
    origine_france: Decimal | None
    titulaires: list[StructureDto]
    considerations_sociales_as_str: list[ConsiderationsSociales] = Field(
        serialization_alias="considerations_sociales"
    )
    considerations_environnementales_as_str: list[ConsiderationsEnvironnementales] = (
        Field(serialization_alias="considerations_environnementales")
    )
    # modifications_actes_sous_traitance: list[ModificationSousTraitanceDto]
    modifications: list[ModificationMarcheDto]


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
    uid: int
    type: str
    localisation: str
    message: str


class DecpMalFormeDto(BaseModel):
    uid: int
    decp: Json[dict[str, Any]]
    erreurs: list[ErreurDto]


class StatsErreursDto(BaseModel):
    erreur: str
    nombre: int
    localisation: str


class MarcheProcedureDto(BaseModel):
    procedure: ProcedureMarche | None
    montant: Decimal
    nombre: int

    @field_validator("procedure", mode="before")
    @classmethod
    def transform(cls, v: int | None) -> ProcedureMarche | None:
        return ProcedureMarche.from_db_value(v) if v else None


class MarcheNatureDto(BaseModel):
    mois: str
    nature: int
    montant: Decimal
    nombre: int


class MarcheCcagDto(BaseModel):
    ccag: CCAG | None
    categorie: CategorieMarche
    montant: Decimal
    nombre: int

    @field_validator("ccag", mode="before")
    @classmethod
    def transform_ccag(cls, v: int) -> CCAG:
        return CCAG.from_db_value(v)

    @field_validator("categorie", mode="before")
    @classmethod
    def transform_cat(cls, v: int) -> CategorieMarche:
        return CategorieMarche.from_db_value(v)


class IndicateursDto(BaseModel):
    periode: int | None
    nb_contrats: int
    montant_total: Decimal
    nb_acheteurs: int
    nb_fournisseurs: int
    nb_sous_traitance: int
    nb_innovant: int


class MarcheDepartementDto(BaseModel):
    code: str
    montant: Decimal
    nombre: int


class MarcheCategorieDepartementDto(BaseModel):
    categorie: CategorieMarche
    code: str
    montant: Decimal

    @field_validator("categorie", mode="before")
    @classmethod
    def transform_cat(cls, v: int) -> CategorieMarche:
        return CategorieMarche.from_db_value(v)


class StructureAggMarchesDto(BaseModel):
    structure: StructureDto
    montant: Decimal
    nb_contrats: int


class CategoriesDto(BaseModel):
    categorie: CategorieMarche
    mois: str
    montant: Decimal
    nombre: int

    @field_validator("categorie", mode="before")
    @classmethod
    def transform_cat(cls, v: int) -> CategorieMarche:
        return CategorieMarche.from_db_value(v)
