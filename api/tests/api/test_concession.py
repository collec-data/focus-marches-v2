from tests.factories import ConcessionFactory, VendeurFactory


def test_list_concessions(client):
    ConcessionFactory.create_batch(30)
    concessionnaire = VendeurFactory()
    concession = ConcessionFactory(concessionnaires=[concessionnaire])

    response = client.get("/contrat-concession", params={"limit": 10, "offset": 10})

    assert response.status_code == 200
    assert len(response.json()) == 10

    response = client.get(
        "/contrat-concession",
        params={
            "date_debut": concession.date_publication,
            "date_fin": concession.date_publication,
            "autorite_concedante_uid": concession.autorite_concedante.uid,
            "concessionnaire_uid": concessionnaire.uid,
        },
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["uid"] == concession.uid


def test_get_concession_succes(client):
    concession = ConcessionFactory()

    response = client.get(f"/contrat-concession/{concession.uid}")

    assert response.status_code == 200
    assert response.json()["uid"] == concession.uid
    assert response.json()["id"] == concession.id


def test_get_concession_inconnu(client):
    response = client.get("/contrat-concession/1111")
    assert response.status_code == 404
    assert response.json()["detail"] == "Concession inconnue"
