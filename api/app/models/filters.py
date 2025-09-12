from datetime import date

from pydantic import BaseModel, Field

from .enums import IdentifiantStructure


class FiltreTemporelStructure(BaseModel):
    date_debut: date | None = None
    date_fin: date | None = None
    identifiant_acheteur: str | None = None
    identifiant_vendeur: str | None = None
    type_identifiant: IdentifiantStructure | None = Field(
        default=IdentifiantStructure.SIRET
    )
