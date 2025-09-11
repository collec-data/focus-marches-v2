from ..factories import *


def test_list_concessions(client):
    ConcessionFactory.create_batch(30)
    response = client.get("/contrat-concession")

    assert response.status_code == 200
    assert len(response.json()) == 20
