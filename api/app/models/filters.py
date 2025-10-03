from datetime import date

from pydantic import BaseModel


class FiltreTemporelStructure(BaseModel):
    date_debut: date | None = None
    date_fin: date | None = None
    acheteur_uid: str | None = None
    vendeur_uid: str | None = None
