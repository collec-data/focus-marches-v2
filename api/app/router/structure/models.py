from datetime import date
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel

from app.models.dto import StructureDto
from app.models.enums import CategorieMarche
from app.models.filters import PaginationParams


class StructuresAggChamps(StrEnum):
    MONTANT = "montant"
    NB = "nb_contrats"
    NOM = "nom"


class ParamsStructuresAgg(PaginationParams):
    date_debut: date | None = None
    date_fin: date | None = None
    categorie: CategorieMarche | None = None
    champs_ordre: StructuresAggChamps = StructuresAggChamps.MONTANT
    ordre: int = -1
    filtre: str | None = None


class ParamsAcheteurs(ParamsStructuresAgg):
    vendeur_uid: int | None = None


class ParamsVendeurs(ParamsStructuresAgg):
    acheteur_uid: int | None = None


class StructureAggMarchesDto(BaseModel):
    structure: StructureDto
    montant: Decimal
    nb_contrats: int


class PaginatedStructureAggMarchesDto(BaseModel):
    total: int
    items: list[StructureAggMarchesDto]
