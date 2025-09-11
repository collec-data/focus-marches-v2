import pytest

from app.models.db import DecpMalForme, Erreur


@pytest.fixture
def create_erreurs(db):
    db.add(
        DecpMalForme(
            decp="{}",
            erreurs=[
                Erreur(type="Empty decp", localisation=".", message="Lorem ipsum dolor")
            ],
        )
    )
    db.commit()


def test_list_erreurs(client, create_erreurs):
    response = client.get("/erreurs-import")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert len(response.json()[0]["erreurs"])
