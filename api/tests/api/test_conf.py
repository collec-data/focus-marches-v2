from tests.factories import ConfFactory


def test_get_conf(client):
    ConfFactory(clef="dernier_import", valeur="2026-05-01")

    response = client.get("/conf")

    assert response.status_code == 200
    assert response.json() == {"dernier_import": "2026-05-01"}
