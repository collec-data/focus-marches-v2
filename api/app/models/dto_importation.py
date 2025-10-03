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
    id: int = Field(ge=0)
    dateNotificationModification: str = Field(pattern=r"\d{4}-\d{2}-\d{2}")
    datePublicationDonneesModification: str = Field(pattern=r"\d{4}-\d{2}-\d{2}")
    dureeMois: int | None = Field(ge=1, default=None)
    montant: float | None = Field(ge=0, default=None)
    titulaires: list[dict[str, TitulaireSchema]] | None = None


class ActeSousTraitanceSchema(BaseModel):
    id: int = Field(ge=0)
    sousTraitant: SousTraitantSchema
    dureeMois: int | None = Field(ge=1)  # should not be null
    dateNotification: str = Field(pattern=r"\d{4}-\d{2}-\d{2}")
    datePublicationDonnees: str = Field(pattern=r"\d{4}-\d{2}-\d{2}")
    montant: float = Field(ge=0)
    variationPrix: VariationPrix

    @field_validator("dureeMois", mode="before")
    @classmethod
    def transform(cls, raw: str | int) -> int | None:
        if raw == "NC":
            return None
        return int(raw)


class ModificationActeSousTraitanceSchema(BaseModel):
    id: int = Field(ge=0)
    dureeMois: int | None = Field(ge=1, default=None)
    dateNotificationModificationActeSousTraitance: str = Field(
        pattern=r"\d{4}-\d{2}-\d{2}", alias="dateNotificationModificationSousTraitance"
    )  # alias hors-norme
    montant: float | None = Field(ge=0, default=None)
    datePublicationDonneesModificationActeSousTraitance: str = Field(
        pattern=r"\d{4}-\d{2}-\d{2}", alias="datePublicationDonnees"
    )  # alias hors-norme

    @field_validator("dureeMois", mode="before")
    @classmethod
    def transform(cls, raw: str | int) -> int | None:
        if raw == "NC":
            return None
        return int(raw)


class MarcheSchema(BaseModel):
    id: str = Field(min_length=1, max_length=16)
    acheteur: AcheteurSchema
    nature: NatureMarche
    objet: str = Field(max_length=1_000)
    codeCPV: str = Field(pattern=r"^[0-9]{8}(-[0-9])?$")
    techniques: dict[str, list[TechniqueAchat]]
    modalitesExecution: dict[str, list[ModaliteExecution]]
    idAccordCadre: str | None = None
    marcheInnovant: bool | None  # should not be null
    ccag: CCAG | None = None
    offresRecues: int | None = Field(ge=1)  # should not be null
    attributionAvance: bool | None  # should not be null
    tauxAvance: float = Field(ge=0, le=1)
    typeGroupementOperateurs: TypeGroupementOperateur | None
    sousTraitanceDeclaree: bool | None  # should not be null
    actesSousTraitance: list[dict[str, ActeSousTraitanceSchema]] = []
    procedure: ProcedureMarche | None = None
    lieuExecution: LieuExecutionSchema
    dureeMois: int = Field(ge=1)
    dateNotification: str = Field(pattern=r"\d{4}-\d{2}-\d{2}")
    datePublicationDonnees: str | None = Field(
        pattern=r"\d{4}-\d{2}-\d{2}"
    )  # should not be null
    montant: float = Field(ge=0)
    typesPrix: dict[str, list[TypePrix]]
    formePrix: FormePrix | None = None
    origineUE: float | None = Field(ge=0, le=1, default=None)
    origineFrance: float | None = Field(ge=0, le=1, default=None)
    titulaires: list[dict[str, TitulaireSchema]]
    considerationsSociales: dict[str, list[ConsiderationsSociales]]
    considerationsEnvironnementales: dict[str, list[ConsiderationsEnvironnementales]]
    modificationsActesSousTraitance: list[
        dict[str, ModificationActeSousTraitanceSchema]
    ] = []
    modifications: list[dict[str, ModificationMarcheSchema]] = []

    @field_validator("offresRecues", mode="before")
    @classmethod
    def transform(cls, raw: str | int) -> int | None:
        return None if raw == "NC" else int(raw)


AutoriteConcedanteSchema = AcheteurSchema
ConcessionnaireSchema = TitulaireSchema


class ModificationConcessionSchema(BaseModel):
    id: int = Field(ge=0)
    dateSignatureModification: str = Field(pattern=r"\d{4}-\d{2}-\d{2}")
    datePublicationDonneesModification: str = Field(pattern=r"\d{4}-\d{2}-\d{2}")
    dureeMois: int | None = Field(ge=1, default=None)
    valeurGlobale: float | None = Field(ge=0, default=None)


class TarifSchema(BaseModel):
    intituleTarif: str = Field(max_length=256)
    tarif: float = Field(ge=0)


class DonneeExecutionSchema(BaseModel):
    datePublicationDonneesExecution: str = Field(pattern=r"\d{4}-\d{2}-\d{2}")
    depensesInvestissement: float = Field(ge=0)
    tarifs: list[dict[str, TarifSchema]]


class ConcessionSchema(BaseModel):
    id: str = Field(min_length=1, max_length=16)
    autoriteConcedante: AutoriteConcedanteSchema
    nature: NatureConcession
    objet: str = Field(max_length=1_000)
    procedure: ProcedureConcession  # requis par la norme
    dureeMois: int = Field(ge=1)
    dateSignature: str = Field(pattern=r"\d{4}-\d{2}-\d{2}")
    datePublicationDonnees: str = Field(pattern=r"\d{4}-\d{2}-\d{2}")
    dateDebutExecution: str = Field(pattern=r"\d{4}-\d{2}-\d{2}")
    valeurGlobale: float = Field(ge=0)
    montantSubventionPublique: float = Field(ge=0)
    donneesExecution: list[dict[str, DonneeExecutionSchema]] = []
    concessionnaires: list[dict[str, ConcessionnaireSchema]]
    considerationsSociales: dict[str, list[ConsiderationsSociales]]
    considerationsEnvironnementales: dict[str, list[ConsiderationsEnvironnementales]]
    modifications: list[dict[str, ModificationConcessionSchema]] = []
