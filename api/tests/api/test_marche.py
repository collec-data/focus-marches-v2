from datetime import date
from decimal import Decimal

from app.models import enums
from tests.factories import (
    AcheteurFactory,
    ClauseEnvFactory,
    ClauseSocialeFactory,
    CPVFactory,
    CritereEnvFactory,
    CritereSocialFactory,
    MarcheFactory,
    TechniqueAchatFactory,
    VendeurFactory,
)


def test_list_marche(client):
    ac = MarcheFactory()
    MarcheFactory.create_batch(29)
    marche_recherche = MarcheFactory(
        objet="Achat d'ordinateurs",
        cpv=CPVFactory(code="456"),
        lieu__code="123",
        lieu__type_code=enums.TypeCodeLieu.DEP.db_value,
        forme_prix=enums.FormePrix.FORFAITAIRE.db_value,
        nature=enums.NatureMarche.DEFSEC.db_value,
        procedure=enums.ProcedureMarche.COMPETITIF.db_value,
        montant=42,
        duree_mois=6,
        categorie=enums.CategorieMarche.FOURNITURES.db_value,
        considerations_sociales=[CritereSocialFactory()],
        considerations_environnementales=[CritereEnvFactory()],
        techniques_achat=[TechniqueAchatFactory()],
        accord_cadre=ac,
    )

    response = client.get("/marche")

    assert response.status_code == 200
    assert len(response.json()) == 31

    response = client.get(
        "/marche",
        params={
            "objet": "ordinateur",
            "cpv": 45,
            "code_lieu": marche_recherche.lieu.code,
            "forme_prix": enums.FormePrix.FORFAITAIRE.value,
            "type_marche": enums.NatureMarche.DEFSEC.value,
            "procedure": enums.ProcedureMarche.COMPETITIF.value,
            "categorie": enums.CategorieMarche.FOURNITURES.value,
            "technique_achat": enums.TechniqueAchat.CONCOURS.value,
            "consideration": enums.ConsiderationsEnvironnementales.CRITERE.value,
            "montant_max": 42,
            "montant_min": 42,
            "duree_max": 6,
            "duree_min": 6,
            "accord_cadre_uid": ac.uid,
            "offset": 0,
            "limit": 100,
        },
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["uid"] == marche_recherche.uid
    assert response.json()[0]["montant_max_accord_cadre"] == str(ac.montant)


def test_procedure_et_filtres_succes(client):
    acheteur = AcheteurFactory()
    vendeur = VendeurFactory()
    MarcheFactory.create_batch(
        1,
        procedure=None,
        montant=Decimal(5),
        acheteur=acheteur,
        date_notification=date(2025, 1, 1),
        titulaires=[vendeur],
    )
    MarcheFactory.create_batch(
        2,
        procedure=enums.ProcedureMarche.ADAPTE.db_value,
        montant=Decimal(3),
        acheteur=acheteur,
        date_notification=date(2025, 1, 1),
        titulaires=[vendeur],
    )
    MarcheFactory.create_batch(
        3,
        procedure=enums.ProcedureMarche.AO_OUVERT.db_value,
        montant=Decimal(4),
        acheteur=acheteur,
        date_notification=date(2025, 1, 1),
        titulaires=[vendeur],
    )

    # les marchés suivants sont hors filtres et ne doivent pas êtres comptabilisés
    MarcheFactory.create(
        titulaires=[vendeur],
        date_notification=date(2025, 1, 1),
    )  # ...car acheteur différent
    MarcheFactory.create(acheteur=acheteur)  # car vendeur différent
    MarcheFactory.create(
        date_notification=date(2000, 1, 1),
        titulaires=[vendeur],
        acheteur=acheteur,
    )  # ...car trop ancien
    MarcheFactory.create(
        date_notification=date(2026, 1, 1),
        titulaires=[vendeur],
        acheteur=acheteur,
    )  # ...car trop récent

    response = client.get(
        "/marche/procedure",
        params={
            "acheteur_uid": acheteur.uid,
            "vendeur_uid": vendeur.uid,
            "date_debut": "2019-01-01",
            "date_fin": "2025-07-01",
        },
    )

    assert response.status_code == 200
    assert response.json() == [
        {"procedure": "Procédure adaptée", "montant": "6", "nombre": 2},
        {"procedure": "Appel d'offres ouvert", "montant": "12", "nombre": 3},
        {"procedure": None, "montant": "5", "nombre": 0},
    ]


def test_nature_succes(client):
    n1 = enums.NatureMarche.MARCHE.db_value
    n2 = enums.NatureMarche.PARTENARIAT.db_value
    MarcheFactory(nature=n1, montant=3, date_notification=date(2025, 12, 1))
    MarcheFactory(nature=n1, montant=4, date_notification=date(2025, 12, 10))
    MarcheFactory(nature=n1, montant=5, date_notification=date(2025, 11, 25))
    MarcheFactory(nature=n2, montant=1, date_notification=date(2025, 12, 1))

    response = client.get("/marche/nature")

    assert response.status_code == 200
    assert response.json() == [
        {"mois": "2025-11", "nature": 1, "montant": "5", "nombre": 1},
        {"mois": "2025-12", "nature": 1, "montant": "7", "nombre": 2},
        {"mois": "2025-12", "nature": 2, "montant": "1", "nombre": 1},
    ]


def test_ccag_succes(client):
    MarcheFactory.create_batch(10, ccag=enums.CCAG.TRAVAUX.db_value, montant=1)
    MarcheFactory.create_batch(8, ccag=enums.CCAG.MO.db_value, montant=2)
    MarcheFactory(
        ccag=enums.CCAG.MO.db_value,
        montant=9,
        categorie=enums.CategorieMarche.TRAVAUX.db_value,
    )

    response = client.get("/marche/ccag")

    assert response.status_code == 200
    assert response.json() == [
        {
            "ccag": "Maitrise d'œuvre",
            "montant": "16",
            "nombre": 8,
            "categorie": "Services",
        },
        {"ccag": "Travaux", "montant": "10", "nombre": 10, "categorie": "Services"},
        {
            "ccag": "Maitrise d'œuvre",
            "montant": "9",
            "nombre": 1,
            "categorie": "Travaux",
        },
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
        6,
        sous_traitance_declaree=True,
        montant=100,
        date_notification=date(2025, 1, 1),
    )

    MarcheFactory(
        sous_traitance_declaree=True,
        montant=100,
        date_notification=date(2025, 1, 1),
        considerations_environnementales=[CritereEnvFactory()],
    )
    MarcheFactory(
        sous_traitance_declaree=True,
        montant=100,
        date_notification=date(2025, 1, 1),
        considerations_environnementales=[CritereEnvFactory()],
        considerations_sociales=[CritereSocialFactory()],
    )
    MarcheFactory(
        sous_traitance_declaree=True,
        montant=100,
        date_notification=date(2025, 1, 1),
        considerations_sociales=[CritereSocialFactory()],
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
        "montant_total": "5400",
        "nb_acheteurs": 45,
        "nb_contrats": 54,
        "nb_fournisseurs": 3,
        "nb_innovant": 10,
        "nb_sous_traitance": 9,
        "periode": 2,
        "nb_considerations_sociale_env": 1,
        "nb_considerations_env": 2,
        "nb_considerations_sociales": 2,
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
        {"code": "35", "montant": "50", "nombre": 5},
        {"code": "29", "montant": "66", "nombre": 2},
    ]


def test_marche_departement_categorie(client):
    MarcheFactory(
        montant=1000,
        categorie=enums.CategorieMarche.TRAVAUX.db_value,
        lieu__code="35",
        lieu__type_code=enums.TypeCodeLieu.DEP.db_value,
    )

    MarcheFactory(
        montant=2000,
        categorie=enums.CategorieMarche.TRAVAUX.db_value,
        lieu__code="35",
        lieu__type_code=enums.TypeCodeLieu.DEP.db_value,
    )

    MarcheFactory(
        montant=5000,
        categorie=enums.CategorieMarche.TRAVAUX.db_value,
        lieu__code="44",
        lieu__type_code=enums.TypeCodeLieu.DEP.db_value,
    )

    MarcheFactory(
        montant=6000,
        categorie=enums.CategorieMarche.FOURNITURES.db_value,
        lieu__code="35",
        lieu__type_code=enums.TypeCodeLieu.DEP.db_value,
    )

    response = client.get("marche/categorie-departement")

    assert response.status_code == 200
    assert response.json() == [
        {"categorie": "Travaux", "code": "35", "montant": "3000"},
        {"categorie": "Travaux", "code": "44", "montant": "5000"},
        {"categorie": "Fournitures", "code": "35", "montant": "6000"},
    ]


def test_categories(client):
    MarcheFactory.create(
        categorie=enums.CategorieMarche.TRAVAUX.db_value,
        date_notification=date(2025, 1, 1),
        montant=10,
    )
    MarcheFactory.create(
        categorie=enums.CategorieMarche.TRAVAUX.db_value,
        date_notification=date(2025, 2, 1),
        montant=1,
    )
    MarcheFactory.create(
        categorie=enums.CategorieMarche.TRAVAUX.db_value,
        date_notification=date(2025, 2, 1),
        montant=2,
    )
    MarcheFactory.create(
        categorie=enums.CategorieMarche.FOURNITURES.db_value,
        date_notification=date(2025, 2, 1),
        montant=4,
    )
    response = client.get("/marche/categorie")

    assert response.status_code == 200
    data = response.json()
    assert data == [
        {"categorie": "Travaux", "mois": "2025-01", "montant": "10", "nombre": 1},
        {"categorie": "Travaux", "mois": "2025-02", "montant": "3", "nombre": 2},
        {"categorie": "Fournitures", "mois": "2025-02", "montant": "4", "nombre": 1},
    ]


def test_get_consideration(client):
    MarcheFactory(
        date_notification=date(2025, 2, 1),
    )
    MarcheFactory(
        considerations_sociales=[CritereSocialFactory()],
        considerations_environnementales=[],
        date_notification=date(2025, 2, 1),
    )
    MarcheFactory(
        considerations_sociales=[CritereSocialFactory()],
        considerations_environnementales=[CritereEnvFactory()],
        date_notification=date(2025, 2, 1),
    )
    MarcheFactory(
        considerations_sociales=[],
        considerations_environnementales=[ClauseEnvFactory()],
        date_notification=date(2025, 2, 1),
    )

    MarcheFactory(
        considerations_sociales=[],
        considerations_environnementales=[CritereEnvFactory()],
        date_notification=date(2025, 2, 1),
    )

    response = client.get("/marche/consideration")

    assert response.status_code == 200
    assert response.json() == [
        {
            "consideration": "Aucune considération",
            "data": [{"nombre": 1, "annee": "2025"}],
        },
        {
            "consideration": "Considération sociale uniquement",
            "data": [{"nombre": 1, "annee": "2025"}],
        },
        {
            "consideration": "Considération environnementale uniquement",
            "data": [{"nombre": 2, "annee": "2025"}],
        },
        {
            "consideration": "Considération sociale et environnementale",
            "data": [{"nombre": 1, "annee": "2025"}],
        },
    ]


def test_get_consideration_environnementale(client):
    MarcheFactory()
    MarcheFactory(
        considerations_sociales=[CritereSocialFactory()],
        considerations_environnementales=[CritereEnvFactory()],
    )
    MarcheFactory(
        considerations_environnementales=[ClauseEnvFactory()],
    )
    MarcheFactory.create(
        considerations_environnementales=[CritereEnvFactory()],
    )
    MarcheFactory.create(
        considerations_environnementales=[CritereEnvFactory()],
    )

    response = client.get("/marche/consideration/environnementale")

    assert response.status_code == 200
    assert response.json() == [
        {"consideration": "Pas de considération environnementale", "nombre": 1},
        {"consideration": "Clause environnementale", "nombre": 1},
        {"consideration": "Critère environnemental", "nombre": 2},
    ]


def test_get_consideration_sociale(client):
    MarcheFactory()
    MarcheFactory(
        considerations_sociales=[CritereSocialFactory()],
        considerations_environnementales=[CritereEnvFactory()],
    )
    MarcheFactory(
        considerations_sociales=[ClauseSocialeFactory()],
    )
    MarcheFactory.create(
        considerations_sociales=[CritereSocialFactory()],
    )
    MarcheFactory.create(
        considerations_sociales=[CritereSocialFactory()],
    )

    response = client.get("/marche/consideration/sociale")

    assert response.status_code == 200
    assert response.json() == [
        {"consideration": "Pas de considération sociale", "nombre": 1},
        {"consideration": "Clause sociale", "nombre": 1},
        {"consideration": "Critère social", "nombre": 2},
    ]


def test_get_consideration_combine(client):
    MarcheFactory()
    MarcheFactory(
        considerations_sociales=[CritereSocialFactory()],
        considerations_environnementales=[CritereEnvFactory()],
    )
    MarcheFactory(
        considerations_sociales=[ClauseSocialeFactory()],
        considerations_environnementales=[CritereEnvFactory()],
    )
    response = client.get("/marche/consideration/combine")

    assert response.status_code == 200
    assert response.json() == [
        {"consideration": "Clause environnementale et sociale", "nombre": 0},
        {"consideration": "Critère environnemental et social", "nombre": 1},
        {"consideration": "Pas de considérations", "nombre": 2},
    ]


def test_get_marche_succes(client):
    marche = MarcheFactory()

    response = client.get(f"/marche/{marche.uid}")

    assert response.status_code == 200
    assert response.json()["uid"] == marche.uid
    assert response.json()["id"] == marche.id


def test_get_marche_inconnu(client):
    response = client.get("/marche/1111")
    assert response.status_code == 404
    assert response.json()["detail"] == "Marche inconnu"
