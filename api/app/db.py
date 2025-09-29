from sqlalchemy import create_engine, Engine

from .models.db import Base
from .config import get_config


def get_engine() -> Engine:
    engine = create_engine(get_config().DATABASE_URL, echo=False)
    Base.metadata.create_all(engine)
    return engine
