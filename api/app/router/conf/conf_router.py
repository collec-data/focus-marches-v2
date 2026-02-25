from fastapi import APIRouter
from sqlalchemy import select

from app.dependencies import SessionDep
from app.models.db import Conf

from .models import ConfDto

router = APIRouter()


@router.get("/")
def get_conf(session: SessionDep) -> ConfDto:
    return ConfDto(
        **{
            ligne.clef: ligne.valeur
            for ligne in list(session.execute(select(Conf)).scalars())
        }
    )
