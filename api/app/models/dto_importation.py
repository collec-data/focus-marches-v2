from datetime import date
from pydantic import BaseModel, Field, field_validator

from app.models.enums import (
    CCAG,
    ConsiderationsEnvironnementales,
    ConsiderationsSociales,
    FormePrix,
    IdentifiantStructure,
    ModaliteExecution,
    NatureConcession,
    NatureMarche,
    ProcedureConcession,
    ProcedureMarche,
    TechniqueAchat,
    TypeCodeLieu,
    TypeGroupementOperateur,
    TypePrix,
    VariationPrix,
)


date_min = date(2000, 1, 1)


class AcheteurSchema(BaseModel):
    id: str = Field(pattern=r"^[0-9]{14}$")  # SIRET


class LieuExecutionSchema(BaseModel):
    code: str
    typeCode: TypeCodeLieu


class TitulaireSchema(BaseModel):
    typeIdentifiant: IdentifiantStructure
    id: str


SousTraitantSchema = TitulaireSchema


class ModificationMarcheSchema(BaseModel):
    id: int = Field(ge=1)
    dateNotificationModification: date = Field(ge=date_min)
    datePublicationDonneesModification: date = Field(ge=date_min)
    dureeMois: int | None = Field(ge=1, default=None)
    montant: float | None = Field(ge=1, default=None)
    titulaires: list[dict[str, TitulaireSchema]] | None = None


class ActeSousTraitanceSchema(BaseModel):
    id: int = Field(ge=1)
    sousTraitant: SousTraitantSchema
    dureeMois: int = Field(ge=1)
    dateNotification: date = Field(ge=date_min)
    datePublicationDonnees: date = Field(ge=date_min)
    montant: float = Field(ge=1)
    variationPrix: VariationPrix


class ModificationActeSousTraitanceSchema(BaseModel):
    id: int = Field(ge=1)
    dureeMois: int | None = Field(ge=1, default=None)
    dateNotificationModificationSousTraitance: date = Field(ge=date_min)
    montant: float | None = Field(ge=1, default=None)
    datePublicationDonnees: date = Field(ge=date_min)

    @field_validator("dureeMois", mode="before")
    @classmethod
    def transform(cls, raw: str | int) -> int | None:
        if raw == "NC":
            return None
        return int(raw)


class MarcheCommunSchema(BaseModel):
    id: str = Field(min_length=1, max_length=16)
    acheteur: AcheteurSchema
    nature: NatureMarche
    objet: str = Field(max_length=1_000)
    codeCPV: str = Field(pattern=r"^[0-9]{8}(-[0-9])?$")
    techniques: dict[str, list[TechniqueAchat]]
    modalitesExecution: dict[str, list[ModaliteExecution]]
    idAccordCadre: str | None = None
    tauxAvance: float | None = Field(ge=0, le=1, default=None)
    actesSousTraitance: list[dict[str, ActeSousTraitanceSchema]] = []
    lieuExecution: LieuExecutionSchema
    dureeMois: int = Field(ge=1)
    dateNotification: date = Field(ge=date_min)
    datePublicationDonnees: date = Field(ge=date_min)
    montant: float = Field(ge=1)
    typesPrix: dict[str, list[TypePrix]]
    origineUE: float | None = Field(ge=0, le=1, default=None)
    origineFrance: float | None = Field(ge=0, le=1, default=None)
    titulaires: list[dict[str, TitulaireSchema]]
    considerationsSociales: dict[str, list[ConsiderationsSociales]]
    considerationsEnvironnementales: dict[str, list[ConsiderationsEnvironnementales]]
    modificationsActesSousTraitance: list[
        dict[str, ModificationActeSousTraitanceSchema]
    ] = []
    modifications: list[dict[str, ModificationMarcheSchema]] = []


class MarcheSchema(MarcheCommunSchema):
    marcheInnovant: bool
    ccag: CCAG
    offresRecues: int = Field(ge=1)
    attributionAvance: bool
    typeGroupementOperateurs: TypeGroupementOperateur
    sousTraitanceDeclaree: bool
    procedure: ProcedureMarche
    formePrix: FormePrix


class MarcheAncienSchema(MarcheCommunSchema):
    marcheInnovant: bool | None
    ccag: CCAG | None = None
    offresRecues: int | None = Field(ge=1, default=None)
    attributionAvance: bool | None
    typeGroupementOperateurs: TypeGroupementOperateur | None
    sousTraitanceDeclaree: bool | None
    procedure: ProcedureMarche | None = None
    formePrix: FormePrix | None = None

    @field_validator("offresRecues", mode="before")
    @classmethod
    def transform(cls, raw: str | int) -> int | None:
        return None if raw == "NC" else int(raw)


AutoriteConcedanteSchema = AcheteurSchema
ConcessionnaireSchema = TitulaireSchema


class ModificationConcessionSchema(BaseModel):
    id: int = Field(ge=0)
    dateSignatureModification: date = Field(ge=date_min)
    datePublicationDonneesModification: date = Field(ge=date_min)
    dureeMois: int | None = Field(ge=1, default=None)
    valeurGlobale: float | None = Field(ge=0, default=None)


class TarifSchema(BaseModel):
    intituleTarif: str = Field(max_length=256)
    tarif: float = Field(ge=0)


class DonneeExecutionSchema(BaseModel):
    datePublicationDonneesExecution: date = Field(ge=date_min)
    depensesInvestissement: float = Field(ge=0)
    tarifs: list[dict[str, TarifSchema]]


class ConcessionSchema(BaseModel):
    id: str = Field(min_length=1, max_length=16)
    autoriteConcedante: AutoriteConcedanteSchema
    nature: NatureConcession
    objet: str = Field(max_length=1_000)
    procedure: ProcedureConcession
    dureeMois: int = Field(ge=1)
    dateSignature: date = Field(ge=date_min)
    datePublicationDonnees: date = Field(ge=date_min)
    dateDebutExecution: date = Field(ge=date_min)
    valeurGlobale: float = Field(ge=1)
    montantSubventionPublique: float = Field(ge=0)
    donneesExecution: list[dict[str, DonneeExecutionSchema]] = []
    concessionnaires: list[dict[str, ConcessionnaireSchema]]
    considerationsSociales: dict[str, list[ConsiderationsSociales]]
    considerationsEnvironnementales: dict[str, list[ConsiderationsEnvironnementales]]
    modifications: list[dict[str, ModificationConcessionSchema]] = []
