from datetime import date

from pydantic import BaseModel, Field

from .enums import IdentifiantStructure


class FiltreTemporelStructure(BaseModel):
    date_debut: date | None = None
    date_fin: date | None = None
    acheteur_uid: str | None = None
    vendeur_uid: str | None = None
