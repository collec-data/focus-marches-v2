from typing import Annotated, Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from .config import get_config, Config
from .db import get_engine


def get_db() -> Generator[Session, None, None]:
    with Session(get_engine()) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]

ConfigDep = Annotated[Config, Depends(get_config)]
