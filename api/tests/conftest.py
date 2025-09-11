from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import pytest

from .factories import *
from app.main import app
from app.models.db import Base
from app.dependencies import get_db


@pytest.fixture
def client(db):
    def get_session_override():
        return db

    app.dependency_overrides[get_db] = get_session_override
    client = TestClient(app)

    return client


@pytest.fixture(autouse=True, name="db")
def db_fixture():
    """
    Toutes les écritures en base de donnée lors d'un tests sont stockées dans une
    unique transaction qui n'est jamais exécutée et qui sera rollback à la fin
    du test. Il n'y donc aucune sollicitation de la base de donnée et les tests
    en sont d'autant plus rapides.
    """

    engine = create_engine("sqlite:///app/test.db", echo=False)
    Base.metadata.create_all(engine)
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    transaction.rollback()
    session.close()
    connection.close()
    Base.metadata.drop_all(engine)


@pytest.fixture(autouse=True)
def set_factory_db(db):
    for my_factory in [
        MarcheFactory,
        StructureFactory,
        LieuFactory,
        ConcessionFactory,
        AcheteurFactory,
        VendeurFactory,
    ]:
        my_factory._meta.sqlalchemy_session = db
