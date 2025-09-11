from sqlalchemy import create_engine

from .models.db import Base
from .config import config


engine = create_engine(config.DATABASE_URL, echo=False)

Base.metadata.create_all(engine)
