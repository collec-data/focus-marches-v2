from app.models.enums import TypeCodeLieu
from tests.factories import LieuFactory


def test_list_lieux(client):
    LieuFactory.create_batch(10, type_code=TypeCodeLieu.COMMUNE.db_value)
    LieuFactory.create_batch(5, type_code=TypeCodeLieu.DEP.db_value)

    response = client.get("/lieu")

    assert response.status_code == 200
    assert len(response.json()) == 15

    response = client.get("/lieu", params={"type_lieu": TypeCodeLieu.DEP.value})

    assert response.status_code == 200
    assert len(response.json()) == 5
