from app.dependencies import get_api_entreprise
from tests.factories import AcheteurFactory, MarcheFactory, VendeurFactory


def test_list_acheteurs(client):
    acheteurs = AcheteurFactory.create_batch(3)
    MarcheFactory.create_batch(2, acheteur=acheteurs[0], montant=5)
    MarcheFactory(acheteur=acheteurs[1], montant=20)
    MarcheFactory(acheteur=acheteurs[2], montant=1)

    response = client.get("/structure/acheteur", params={"limit": 2})
    assert response.status_code == 200

    assert response.json() == [
        {
            "montant": "20",
            "nb_contrats": 1,
            "structure": {
                "acheteur": True,
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
                "identifiant": acheteurs[0].identifiant,
                "nom": None,
                "type_identifiant": acheteurs[0].type_identifiant,
                "uid": acheteurs[0].uid,
                "vendeur": False,
            },
        },
    ]


def test_list_vendeurs(client):
    vendeurs = VendeurFactory.create_batch(3)
    MarcheFactory.create_batch(2, titulaires=[vendeurs[0]], montant=5)
    MarcheFactory(titulaires=[vendeurs[1]], montant=2)
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


def test_get_structure(client, mocker):
    data_mock = mocker.Mock()
    data_mock.unite_legale.personne_morale_attributs.raison_sociale = "Mon entreprise"
    data_mock.unite_legale.personne_morale_attributs.sigle = "ME"
    data_mock.unite_legale.forme_juridique.code = "1234"
    data_mock.adresse_postale_legere = "Rennes"
    data_mock.unite_legale.activite_principale.code = "00.00Z"
    data_mock.unite_legale.tranche_effectif_salarie.intitule = "20 à 40"
    data_mock.unite_legale.tranche_effectif_salarie.date_reference = "2025"

    mock = mocker.Mock()
    mock.donnees_etablissement.return_value = data_mock
    client.app.dependency_overrides[get_api_entreprise] = lambda: mock

    acheteur = AcheteurFactory(identifiant="9999")
    response = client.get(f"/structure/{acheteur.uid}")

    assert response.status_code == 200
    assert response.json()["sigle"] == "ME"
    mock.donnees_etablissement.assert_called_with(acheteur.identifiant)


def test_get_structure_does_not_exists(client):
    response = client.get("/structure/123456")

    assert response.status_code == 404
    assert response.json()["detail"] == "Structure inconnue"
