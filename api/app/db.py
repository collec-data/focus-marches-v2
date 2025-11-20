from functools import cache

from sqlalchemy import Engine, create_engine

from .config import get_config
from .models.db import Base


@cache
def get_engine() -> Engine:
    engine = create_engine(
        get_config().DATABASE_URL, echo=False, pool_size=5, max_overflow=10
    )
    Base.metadata.create_all(engine)
    return engine
