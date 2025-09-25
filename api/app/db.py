from sqlalchemy import create_engine

from .models.db import Base
from .config import get_config


engine = create_engine(get_config().DATABASE_URL, echo=False)

Base.metadata.create_all(engine)
