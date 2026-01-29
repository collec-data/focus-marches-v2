import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import Config, get_config
from app.dependencies import get_api_entreprise, get_db
from app.main import app
from app.models.db import Base
from tests.factories import (
    AcheteurFactory,
    ClauseEnvFactory,
    ClauseSocialeFactory,
    ConcessionFactory,
    CPVFactory,
    CritereEnvFactory,
    CritereSocialFactory,
    DecpMalFormeFactory,
    ErreurFactory,
    LieuFactory,
    MarcheFactory,
    StructureFactory,
    StructureInfogreffeFactory,
    TechniqueAchatFactory,
    VendeurFactory,
)
from tests.mariadb_testcontainer import MariaDBContainer


@pytest.fixture
def client(db, db_url):
    def get_session_override():
        return db

    def get_config_override():
        return Config(
            DATABASE_URL=db_url,
            API_ENTREPRISE_URL="https://api.entreprise",
            API_ENTREPRISE_TOKEN="MySecret",
        )

    app.dependency_overrides[get_db] = get_session_override
    app.dependency_overrides[get_api_entreprise] = lambda: None
    app.dependency_overrides[get_config] = get_config_override
    client = TestClient(app)

    return client


@pytest.fixture(autouse=True, name="db")
def db_fixture(db_url):
    """
    Toutes les écritures en base de donnée lors d'un tests sont stockées dans une
    unique transaction qui n'est jamais exécutée et qui sera rollback à la fin
    du test. Il n'y donc aucune sollicitation de la base de donnée et les tests
    en sont d'autant plus rapides.
    """

    engine = create_engine(
        db_url,
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
        ErreurFactory,
        DecpMalFormeFactory,
        CritereSocialFactory,
        ClauseSocialeFactory,
        CritereEnvFactory,
        ClauseEnvFactory,
        TechniqueAchatFactory,
        StructureInfogreffeFactory,
        CPVFactory,
    ]:
        my_factory._meta.sqlalchemy_session = db


@pytest.fixture(scope="session", autouse=True)
def db_url():
    """Ensure that database is up and responsive."""

    with MariaDBContainer() as container:
        yield container.get_connection_url().replace("localhost", "127.0.0.1")
