from tests.factories import CPVFactory


def test_list_cpv(client):
    one_cpv = CPVFactory(libelle="anticonstitutionnellemeeeeeeeeent")
    CPVFactory.create_batch(50)

    response = client.get("/cpv")

    assert response.status_code == 200
    assert len(response.json()) == 51

    response = client.get("/cpv", params={"libelle": "tionnellemeeeee"})

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["code"] == one_cpv.code
