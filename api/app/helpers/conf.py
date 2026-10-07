from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.helpers.timezone import TZ_EUROPE_PARIS
from app.models.db import Conf


def create_or_update(session: Session, clef: str, valeur: str) -> None:
    existant = session.execute(select(Conf).where(Conf.clef == clef)).scalar()
    if existant:
        existant.valeur = valeur
    else:
        session.add(Conf(clef=clef, valeur=valeur))

    session.commit()


def set_dernier_import(session: Session) -> None:
    create_or_update(
        session,
        "dernier_import",
        datetime.now(tz=TZ_EUROPE_PARIS).date().strftime("%Y-%m-%d"),
    )
