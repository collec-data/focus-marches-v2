from datetime import date

from pydantic import BaseModel, Field

from app.models.enums import (
    CategorieMarche,
    ConsiderationsEnvironnementales,
    ConsiderationsSociales,
    FormePrix,
    NatureMarche,
    ProcedureMarche,
    TechniqueAchat,
)


class PaginationParams(BaseModel):
    limit: int | None = Field(ge=0, default=None)
    offset: int = Field(ge=0, default=0)


class FiltreTemporelStructure(BaseModel):
    date_debut: date | None = None
    date_fin: date | None = None
    acheteur_uid: int | None = None
    vendeur_uid: int | None = None


class FiltreMarchesEtendus(FiltreTemporelStructure):
    objet: str | None = None
    cpv: str | None = None
    code_lieu: str | None = Field(default=None)
    forme_prix: FormePrix | None = None
    type_marche: NatureMarche | None = None
    procedure: ProcedureMarche | None = None
    categorie: CategorieMarche | None = None
    technique_achat: TechniqueAchat | None = None
    consideration: ConsiderationsEnvironnementales | ConsiderationsSociales | None = (
        None
    )
    montant_max: int | None = Field(ge=0, default=None)
    montant_min: int | None = Field(ge=0, default=None)
    duree_max: int | None = Field(ge=0, default=None)
    duree_min: int | None = Field(ge=0, default=None)


class FiltresListeMarches(FiltreMarchesEtendus, PaginationParams):
    accord_cadre_uid: int | None = Field(default=None)


class FiltreListesConcessions(PaginationParams):
    date_debut: date | None = None
    date_fin: date | None = None
    autorite_concedante_uid: str | None = None
    concessionnaire_uid: str | None = None
