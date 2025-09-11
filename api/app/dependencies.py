from typing import Annotated, Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from .db import engine


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


# Dépendance FastAPI pour la session de base de données.
SessionDep = Annotated[Session, Depends(get_db)]
