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


class FiltreTemporelStructure(BaseModel):
    date_debut: date | None = None
    date_fin: date | None = None
    acheteur_uid: str | None = None
    vendeur_uid: str | None = None


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


class FiltresListeMarches(FiltreMarchesEtendus):
    limit: int | None = Field(default=None, gt=0)
    offset: int | None = Field(default=None, ge=0)


class FiltreListesConcessions(BaseModel):
    limit: int | None = Field(default=None, gt=0)
    offset: int | None = Field(default=None, ge=0)
    date_debut: date | None = None
    date_fin: date | None = None
    autorite_concedante_uid: str | None = None
    concessionnaire_uid: str | None = None
