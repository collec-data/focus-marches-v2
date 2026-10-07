from functools import cache

from sqlalchemy import Engine, create_engine

from .config import get_config


@cache
def get_engine() -> Engine:
    engine = create_engine(
        get_config().DATABASE_URL,
        echo=False,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        # pool_recycle doit être inférieur à la valeur de wait_timeout configurée sur mariadb
        # (le délai à partir duquel mariadb ferme les connexions innocupées ; par défaut 28 800 secondes, soit 8h)
        pool_recycle=27_000,
    )
    return engine
