from typing import Annotated, Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from .config import get_config, Config
from .db import engine


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]

ConfigDep = Annotated[Config, Depends(get_config)]
