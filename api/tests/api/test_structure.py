from tests.factories import *


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
