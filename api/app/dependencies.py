from collections.abc import Generator
from typing import Annotated

from api_entreprise.api import ApiEntreprise
from api_entreprise.models.config import Config as APIEntrepriseConfig
from api_entreprise.models.context_info import ContextInfo
from fastapi import Depends
from pyrate_limiter import Limiter, RequestRate
from sqlalchemy.orm import Session

from app.config import Config, get_config
from app.db import get_engine


def get_db() -> Generator[Session, None, None]:
    with Session(get_engine()) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]

ConfigDep = Annotated[Config, Depends(get_config)]


def get_api_entreprise(config: ConfigDep) -> ApiEntreprise:
    confif_api = APIEntrepriseConfig(
        base_url=config.API_ENTREPRISE_URL,
        token=config.API_ENTREPRISE_TOKEN,
        default_context_info=ContextInfo(context="", recipient="", object=""),
        rate_limiter=Limiter(RequestRate(10000, 60)),  # pas besoin de ménager notre API
    )
    return ApiEntreprise(confif_api)


ApiEntrepriseDep = Annotated[ApiEntreprise, Depends(get_api_entreprise)]
