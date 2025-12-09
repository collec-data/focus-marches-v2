from app.dependencies import get_api_entreprise
from app.helpers.opendatasoft import get_opendatasoft
from tests.factories import AcheteurFactory, MarcheFactory, VendeurFactory


def test_list_structures(client):
    AcheteurFactory.create_batch(9)
    AcheteurFactory(nom="COMMUNAUTE DE COMMUNE DE ")
    VendeurFactory.create_batch(20, nom="COMMUNE DE")

    response = client.get("/structure/")

    assert response.status_code == 200
    assert len(response.json()) == 30

    response = client.get("/structure/", params={"is_acheteur": True})

    assert response.status_code == 200
    assert len(response.json()) == 10

    response = client.get("/structure/", params={"is_vendeur": True})

    assert response.status_code == 200
    assert len(response.json()) == 20

    response = client.get("/structure/", params={"nom": "COMMUNE"})

    assert response.status_code == 200
    assert len(response.json()) == 21


def test_list_acheteurs(client):
    titulaire1 = VendeurFactory()
    titulaire2 = VendeurFactory()
    acheteurs = AcheteurFactory.create_batch(3)
    MarcheFactory.create_batch(
        2, acheteur=acheteurs[0], montant=5, titulaires=[titulaire1, titulaire2]
    )
    marche = MarcheFactory(acheteur=acheteurs[1], montant=20, titulaires=[titulaire1])
    MarcheFactory(acheteur=acheteurs[2], montant=1, titulaires=[titulaire2])

    response = client.get("/structure/acheteur", params={"limit": 2})
    assert response.status_code == 200

    assert response.json() == [
        {
            "montant": "20",
            "nb_contrats": 1,
            "structure": {
                "acheteur": True,
                "cat_entreprise": None,
                "identifiant": acheteurs[1].identifiant,
                "nom": None,
                "type_identifiant": acheteurs[1].type_identifiant,
                "uid": acheteurs[1].uid,
                "vendeur": False,
            },
        },
        {
            "montant": "10",
            "nb_contrats": 2,
            "structure": {
                "acheteur": True,
                "cat_entreprise": None,
                "identifiant": acheteurs[0].identifiant,
                "nom": None,
                "type_identifiant": acheteurs[0].type_identifiant,
                "uid": acheteurs[0].uid,
                "vendeur": False,
            },
        },
    ]

    response = client.get("/structure/acheteur", params={"vendeur_uid": titulaire2.uid})
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert {
        response.json()[0]["structure"]["uid"],
        response.json()[1]["structure"]["uid"],
    } == {acheteurs[0].uid, acheteurs[2].uid}

    response = client.get(
        "/structure/acheteur",
        params={
            "date_debut": marche.date_notification,
            "date_fin": marche.date_notification,
            "limit": 10,
        },
    )
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_list_vendeurs(client):
    vendeurs = VendeurFactory.create_batch(3)
    acheteur = AcheteurFactory()
    MarcheFactory.create_batch(
        2, titulaires=[vendeurs[0]], montant=5, acheteur=acheteur
    )
    marche = MarcheFactory(titulaires=[vendeurs[1]], montant=2, acheteur=acheteur)
    MarcheFactory(titulaires=vendeurs, montant=3)

    response = client.get("/structure/vendeur")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 3
    assert data[0]["structure"]["identifiant"] == vendeurs[0].identifiant
    assert data[0]["nb_contrats"] == 3
    assert data[0]["montant"] == "13"

    assert data[1]["structure"]["identifiant"] == vendeurs[1].identifiant
    assert data[1]["nb_contrats"] == 2
    assert data[1]["montant"] == "5"

    assert data[2]["structure"]["identifiant"] == vendeurs[2].identifiant
    assert data[2]["nb_contrats"] == 1
    assert data[2]["montant"] == "3"

    response = client.get("/structure/vendeur", params={"acheteur_uid": acheteur.uid})
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert {
        response.json()[0]["structure"]["uid"],
        response.json()[1]["structure"]["uid"],
    } == {vendeurs[0].uid, vendeurs[1].uid}

    response = client.get(
        "/structure/vendeur",
        params={
            "date_debut": marche.date_notification,
            "date_fin": marche.date_notification,
            "limit": 10,
        },
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["structure"]["uid"] == vendeurs[1].uid


def test_get_structure(client, mocker):
    data_mock = mocker.Mock()
    data_mock.unite_legale.personne_morale_attributs.raison_sociale = "Mon entreprise"
    data_mock.unite_legale.personne_morale_attributs.sigle = "ME"
    data_mock.unite_legale.forme_juridique.code = "1234"
    data_mock.adresse_postale_legere = "Rennes"
    data_mock.unite_legale.activite_principale.code = "00.00Z"
    data_mock.unite_legale.tranche_effectif_salarie.intitule = "20 à 40"
    data_mock.unite_legale.tranche_effectif_salarie.date_reference = "2025"
    data_mock.date_creation = "123456"

    api_entreprise_mock = mocker.Mock()
    api_entreprise_mock.donnees_etablissement.return_value = data_mock
    client.app.dependency_overrides[get_api_entreprise] = lambda: api_entreprise_mock

    ods_mock = mocker.Mock()
    ods_mock.getCoordonnees.return_value = {"lon": 1, "lat": 2}
    client.app.dependency_overrides[get_opendatasoft] = lambda: ods_mock

    acheteur = AcheteurFactory(identifiant="9999")
    response = client.get(f"/structure/{acheteur.uid}")

    assert response.status_code == 200
    assert response.json()["sigle"] == "ME"
    api_entreprise_mock.donnees_etablissement.assert_called_with(acheteur.identifiant)
    ods_mock.getCoordonnees.assert_called_with(acheteur.identifiant)


def test_get_structure_does_not_exists(client):
    response = client.get("/structure/123456")

    assert response.status_code == 404
    assert response.json()["detail"] == "Structure inconnue"
