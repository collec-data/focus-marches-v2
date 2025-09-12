from decimal import Decimal
from datetime import date

from tests.factories import *


def test_list_marche(client):
    MarcheFactory.create_batch(30)
    response = client.get("/marche")

    assert response.status_code == 200
    assert len(response.json()) == 20


def test_procedure_et_filtres_succes(client):
    acheteur_id = "1234"
    titulaire_id = "9876"
    MarcheFactory.create_batch(
        1,
        procedure=None,
        montant=Decimal(5),
        acheteur__identifiant=acheteur_id,
        date_notification=date(2025, 1, 1),
        titulaires=[VendeurFactory.create(identifiant=titulaire_id)],
    )
    MarcheFactory.create_batch(
        2,
        procedure=1,
        montant=Decimal(3),
        acheteur__identifiant=acheteur_id,
        date_notification=date(2025, 1, 1),
        titulaires=[VendeurFactory.create(identifiant=titulaire_id)],
    )
    MarcheFactory.create_batch(
        3,
        procedure=2,
        montant=Decimal(4),
        acheteur__identifiant=acheteur_id,
        date_notification=date(2025, 1, 1),
        titulaires=[VendeurFactory.create(identifiant=titulaire_id)],
    )

    # les marchés suivants sont hors filtres et ne doivent pas êtres comptabilisés
    MarcheFactory.create(
        titulaires=[VendeurFactory.create(identifiant=titulaire_id)],
        date_notification=date(2025, 1, 1),
    )  # ...car acheteur différent
    MarcheFactory.create(acheteur__identifiant=acheteur_id)  # car vendeur différent
    MarcheFactory.create(
        date_notification=date(2000, 1, 1),
        titulaires=[VendeurFactory.create(identifiant=titulaire_id)],
        acheteur__identifiant=acheteur_id,
    )  # ...car trop ancien
    MarcheFactory.create(
        date_notification=date(2026, 1, 1),
        titulaires=[VendeurFactory.create(identifiant=titulaire_id)],
        acheteur__identifiant=acheteur_id,
    )  # ...car trop récent

    response = client.get(
        "/marche/procedure",
        params={
            "identifiant_acheteur": acheteur_id,
            "identifiant_vendeur": titulaire_id,
            "date_debut": "2019-01-01",
            "date_fin": "2025-07-01",
        },
    )

    assert response.status_code == 200
    assert response.json() == [
        {"procedure": None, "montant": "5.0000000000", "nombre": 0},
        {"procedure": 1, "montant": "6.0000000000", "nombre": 2},
        {"procedure": 2, "montant": "12.0000000000", "nombre": 3},
    ]


# ToDo: move to PGSQL
# def test_nature_succes(client):
#     response = client.get("/marche/nature")

#     assert response.status_code == 200
#     assert response.json() == []


def test_ccag_succes(client):
    print(MarcheFactory.create_batch(10, ccag=1, montant=1))
    MarcheFactory.create_batch(8, ccag=2, montant=2)

    response = client.get("/marche/ccag")

    assert response.status_code == 200
    assert response.json() == [
        {"ccag": 1, "montant": "10.0000000000", "nombre": 10},
        {"ccag": 2, "montant": "16.0000000000", "nombre": 8},
    ]


def test_indicateurs_succes(client):
    MarcheFactory.create_batch(
        35,
        montant=100,
        titulaires=[AcheteurFactory()],
        date_notification=date(2025, 1, 1),
    )
    MarcheFactory.create_batch(
        10,
        marche_innovant=True,
        montant=100,
        acheteur=AcheteurFactory(),
        titulaires=[AcheteurFactory(), AcheteurFactory()],
        date_notification=date(2025, 1, 1),
    )
    MarcheFactory.create_batch(
        9, sous_traitance_declaree=True, montant=100, date_notification=date(2025, 1, 1)
    )

    response = client.get(
        "/marche/indicateurs",
        params={
            "date_debut": "2024-12-01",
            "date_fin": "2025-02-01",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "montant_total": "5400.0000000000",
        "nb_acheteurs": 45,
        "nb_contrats": 54,
        "nb_fournisseurs": 3,
        "nb_innovant": 10,
        "nb_sous_traitance": 9,
        "periode": 2,
    }


def test_departements(client):
    MarcheFactory.create_batch(
        5,
        montant=10,
        lieu__code="35",
        lieu__type_code=enums.TypeCodeLieu.DEP.db_value,
    )
    MarcheFactory.create_batch(
        2,
        montant=33,
        lieu__code="29",
        lieu__type_code=enums.TypeCodeLieu.DEP.db_value,
    )

    # pas un département, ne doit pas être comptabilisé
    MarcheFactory.create_batch(
        1,
        montant=1000,
        lieu__code="123",
        lieu__type_code=enums.TypeCodeLieu.COMMUNE.db_value,
    )

    response = client.get("/marche/departement")

    assert response.status_code == 200
    assert response.json() == [
        {"code": "29", "montant": "66.0000000000", "nombre": 2},
        {"code": "35", "montant": "50.0000000000", "nombre": 5},
    ]
