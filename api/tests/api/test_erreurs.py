from tests.factories import DecpMalFormeFactory


def test_list_erreurs(client):
    localisation = "lorem.ipsum.dolor"
    decp = DecpMalFormeFactory(erreurs__0__localisation=localisation)
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

    response = client.get(
        "/erreurs-import",
        params={
            "localisation": localisation,
            "type": "Erreur générique",
            "uid_structure": decp.structure.uid if decp.structure else None,
            "date_debut": decp.date_creation,
            "date_fin": decp.date_creation,
        },
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["uid"] == decp.uid


def test_list_erreurs_plusieurs_erreurs_pas_de_doublon(client):
    decp = DecpMalFormeFactory()

    response = client.get("/erreurs-import")

    assert [d["uid"] for d in response.json()] == [decp.uid]
    assert len(response.json()[0]["erreurs"]) == 2


def test_list_erreurs_filtre_sur_erreur_multiple_pas_de_doublon(client):
    decp = DecpMalFormeFactory()

    response = client.get("/erreurs-import", params={"type": "Erreur générique"})

    assert [d["uid"] for d in response.json()] == [decp.uid]


def test_list_erreurs_limite_compte_des_decp(client):
    DecpMalFormeFactory.create_batch(4)

    response = client.get("/erreurs-import", params={"limit": 3})

    assert len({d["uid"] for d in response.json()}) == 3
    assert len(response.json()) == 3


def test_list_erreurs_filtres_type_et_localisation_sur_la_meme_erreur(client):
    DecpMalFormeFactory(
        erreurs__0__type="A",
        erreurs__0__localisation="a",
        erreurs__1__type="B",
        erreurs__1__localisation="b",
    )

    response = client.get("/erreurs-import", params={"type": "A", "localisation": "b"})

    assert response.json() == []


def test_get_stats_aucune_erreur(client):
    response = client.get("/erreurs-import/stats")

    assert response.status_code == 200
    assert response.json() == []


def test_get_stats(client):
    # La factory DecpMalForme genère des objets avec deux erreurs pour chaque DECP.
    # On va utiliser la première pour tester l'agrégation sur la localisation
    # et la seconde pour l'agrégation sur le message d'erreur

    one_decp = DecpMalFormeFactory.create_batch(
        5,
        erreurs__0__localisation="montant",
        erreurs__1__message="Erreur Une",
    )[0]
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

    response = client.get(
        "/erreurs-import/stats",
        params={
            "uid_structure": one_decp.structure.uid,
            "date_debut": one_decp.date_creation,
            "date_fin": one_decp.date_creation,
        },
    )

    assert response.status_code == 200
    # on a un unique DECP qui correspond à tout les critères
    # et il contient deux erreurs différentes
    assert len(response.json()) == 2
    assert response.json()[0]["nombre"] == 1
    assert response.json()[1]["nombre"] == 1
