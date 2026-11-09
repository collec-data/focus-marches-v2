from datetime import date
from decimal import Decimal

from tests.factories import (
    ConcessionFactory,
    DonneeExecutionFactory,
    TarifFactory,
    VendeurFactory,
)


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


def test_get_concession_donnees_execution(client):
    concession = ConcessionFactory(
        donnees_execution=[
            DonneeExecutionFactory(
                date_publication=date(2025, 1, 1),
                depenses_investissement=Decimal(100000),
                tarifs=[
                    TarifFactory(intitule="1 voyage", tarif=Decimal(1)),
                    TarifFactory(intitule="10 voyages", tarif=Decimal(9)),
                ],
            )
        ]
    )

    response = client.get(f"/contrat-concession/{concession.uid}")

    assert response.status_code == 200
    (donnee,) = response.json()["donnees_execution"]
    assert donnee["date_publication"] == "2025-01-01"
    assert Decimal(donnee["depenses_investissement"]) == 100000
    assert [(t["intitule"], Decimal(t["tarif"])) for t in donnee["tarifs"]] == [
        ("1 voyage", 1),
        ("10 voyages", 9),
    ]


def test_list_concessions_donnees_execution(client):
    ConcessionFactory(donnees_execution=[DonneeExecutionFactory()])

    response = client.get("/contrat-concession")

    assert response.status_code == 200
    assert len(response.json()[0]["donnees_execution"]) == 1


def test_get_concession_inconnu(client):
    response = client.get("/contrat-concession/1111")
    assert response.status_code == 404
    assert response.json()["detail"] == "Concession inconnue"


def test_list_concessions_plusieurs_concessionnaires_pas_de_doublon(client):
    concession = ConcessionFactory(concessionnaires=VendeurFactory.create_batch(3))

    response = client.get("/contrat-concession")

    assert [c["uid"] for c in response.json()] == [concession.uid]
    assert len(response.json()[0]["concessionnaires"]) == 3


def test_list_concessions_plusieurs_concessionnaires_limite_compte_des_concessions(
    client,
):
    for _ in range(4):
        ConcessionFactory(concessionnaires=VendeurFactory.create_batch(3))

    response = client.get("/contrat-concession", params={"limit": 3})

    assert len({c["uid"] for c in response.json()}) == 3
    assert len(response.json()) == 3
