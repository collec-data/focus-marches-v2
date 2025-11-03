from tests.factories import DecpMalFormeFactory


def test_list_erreurs(client):
    localisation = "lorem.ipsum.dolor"
    DecpMalFormeFactory(erreurs__0__localisation=localisation)
    DecpMalFormeFactory.create_batch(3)

    response = client.get("/erreurs-import", params={"limit": 2, "offset": 1})

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert len(response.json()[0]["erreurs"])

    response = client.get(
        "/erreurs-import",
        params={"localisation": localisation, "type": "Erreur générique"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_stats_aucune_erreur(client):
    response = client.get("/erreurs-import/stats")

    assert response.status_code == 200
    assert response.json() == []


def test_get_stats(client):
    # La factory DecpMalForme genère des objets avec deux erreurs pour chaque DECP.
    # On va utiliser la première pour tester l'agrégation sur la localisation
    # et la seconde pour l'agrégation sur le message d'erreur

    DecpMalFormeFactory.create_batch(
        5,
        erreurs__0__localisation="montant",
        erreurs__1__message="Erreur Une",
    )
    DecpMalFormeFactory.create_batch(
        1,
        erreurs__0__localisation="montant",
        erreurs__1__message="Erreur Deux",
    )
    DecpMalFormeFactory.create_batch(
        3,
        erreurs__0__localisation="durée",
        erreurs__1__message="Erreur Trois",
    )
    response = client.get("/erreurs-import/stats")

    assert response.status_code == 200
    assert response.json() == [
        {
            "erreur": "Lorem ipsum dolor",
            "localisation": "montant",
            "nombre": 6,
            "type": "Erreur générique",
        },
        {
            "erreur": "Erreur Une",
            "localisation": ".",
            "nombre": 5,
            "type": "Erreur générique",
        },
        {
            "erreur": "Erreur Trois",
            "localisation": ".",
            "nombre": 3,
            "type": "Erreur générique",
        },
        {
            "erreur": "Lorem ipsum dolor",
            "localisation": "durée",
            "nombre": 3,
            "type": "Erreur générique",
        },
        {
            "erreur": "Erreur Deux",
            "localisation": ".",
            "nombre": 1,
            "type": "Erreur générique",
        },
    ]
