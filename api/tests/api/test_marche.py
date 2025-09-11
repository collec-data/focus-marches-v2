from tests.factories import *


def test_list_marche(client):
    MarcheFactory.create_batch(30)
    response = client.get("/marche")

    assert response.status_code == 200
    assert len(response.json()) == 20
