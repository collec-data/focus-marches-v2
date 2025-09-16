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
            "montant": "20.0000000000",
            "structure": {
                "acheteur": True,
                "identifiant": acheteurs[1].identifiant,
                "type_identifiant": acheteurs[1].type_identifiant,
                "uid": acheteurs[1].uid,
                "vendeur": False,
            },
        },
        {
            "montant": "10.0000000000",
            "structure": {
                "acheteur": True,
                "identifiant": acheteurs[0].identifiant,
                "type_identifiant": acheteurs[0].type_identifiant,
                "uid": acheteurs[0].uid,
                "vendeur": False,
            },
        },
    ]
