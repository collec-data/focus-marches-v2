from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import pytest
import psycopg

from .factories import *
from app.main import app
from app.models.db import Base
from app.dependencies import get_db, get_api_entreprise
from app.config import get_config, Config


@pytest.fixture
def client(db):
    def get_session_override():
        return db

    def get_config_override():
        return Config(
            DATABASE_URL="postgresql+psycopg://postgres:password@localhost:5454/test",
            API_ENTREPRISE_URL="https://api.entreprise",
            API_ENTREPRISE_TOKEN="MySecret",
        )

    app.dependency_overrides[get_db] = get_session_override
    app.dependency_overrides[get_api_entreprise] = lambda: None
    app.dependency_overrides[get_config] = get_config_override
    client = TestClient(app)

    return client


@pytest.fixture(autouse=True, name="db")
def db_fixture(db_service):
    """
    Toutes les écritures en base de donnée lors d'un tests sont stockées dans une
    unique transaction qui n'est jamais exécutée et qui sera rollback à la fin
    du test. Il n'y donc aucune sollicitation de la base de donnée et les tests
    en sont d'autant plus rapides.
    """

    engine = create_engine(
        "postgresql+psycopg://postgres:password@localhost:5454/test",
        echo=False,
    )
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


def db_is_responsive():
    try:
        conn = psycopg.connect("postgresql://postgres:password@localhost:5454/test")
        conn.close()
        return True
    except:
        return False


@pytest.fixture(scope="session", autouse=True)
def db_service(docker_services):
    """Ensure that PG database is up and responsive."""
    docker_services.wait_until_responsive(
        timeout=10.0, pause=0.1, check=lambda: db_is_responsive()
    )
