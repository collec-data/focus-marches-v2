from tests.factories import DecpMalFormeFactory


def test_list_erreurs(client):
    DecpMalFormeFactory.create_batch(2)

    response = client.get("/erreurs-import")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert len(response.json()[0]["erreurs"])
