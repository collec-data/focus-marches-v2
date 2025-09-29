from sqlalchemy import create_engine

from .models.db import Base
from .config import get_config


def get_engine():
    engine = create_engine(get_config().DATABASE_URL, echo=False)
    Base.metadata.create_all(engine)
    return engine
