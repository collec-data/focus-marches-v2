from sqlalchemy import create_engine, inspect, text

from app.db import creer_index_manquants

INDEX_MARCHE = "ix_marche_date_notification_uid"


def noms_index(engine, table):
    return {i["name"] for i in inspect(engine).get_indexes(table)}


def test_creer_index_manquants_recree_un_index_supprime(db_url):
    engine = create_engine(db_url)
    with engine.begin() as connexion:
        connexion.execute(text(f"DROP INDEX {INDEX_MARCHE} ON marche"))
    assert INDEX_MARCHE not in noms_index(engine, "marche")

    creer_index_manquants(engine)

    assert INDEX_MARCHE in noms_index(engine, "marche")


def test_creer_index_manquants_est_idempotent(db_url):
    engine = create_engine(db_url)

    creer_index_manquants(engine)
    creer_index_manquants(engine)

    assert INDEX_MARCHE in noms_index(engine, "marche")
