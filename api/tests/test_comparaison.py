import csv
import logging
from datetime import date
from pathlib import Path

import pytest
import typer
from typer.testing import CliRunner

from app.comparaison import (
    MarcheCompare,
    Source,
    Statut,
    app,
    apparier,
    ecrire_csv,
    extraire_marches,
    lire_sirets,
)

FICHIERS = Path("tests/files/comparaison")
SIRETS = {"11111111111111", "33333333333333"}


# La comparaison ne touche pas à la base de données : on neutralise les
# fixtures autouse de conftest.py pour ne pas démarrer le conteneur MariaDB.
@pytest.fixture(scope="module")
def db_url():
    return ""


@pytest.fixture(name="db")
def db_fixture():
    return None


def _par_id(marches):
    return {m.id_marche: m for m in marches}


def test_extraire_marches_filtre_siret():
    marches, stats = extraire_marches(FICHIERS / "daj", Source.DAJ, SIRETS)

    assert stats.fichiers_lus == 1
    assert stats.marches_lus == 7
    assert stats.marches_hors_filtre == 1
    assert "M-HORS-FILTRE" not in _par_id(marches)
    assert len(marches) == 6


def test_extraire_marches_incomparable_sans_titulaire():
    marches, _ = extraire_marches(FICHIERS / "daj", Source.DAJ, SIRETS)

    marche = _par_id(marches)["M-DAJ-8"]
    assert marche.statut is Statut.INCOMPARABLE
    assert marche.raison_incomparable == "aucun titulaire"


def test_appariement_complet():
    marches_daj, _ = extraire_marches(FICHIERS / "daj", Source.DAJ, SIRETS)
    marches_opsn, _ = extraire_marches(FICHIERS / "opsn", Source.OPSN, SIRETS)

    apparier(marches_daj, marches_opsn)
    daj = _par_id(marches_daj)
    opsn = _par_id(marches_opsn)

    # Match exact (mêmes titulaires)
    assert opsn["M-OPSN-1"].statut is Statut.PRESENT_DEUX_COTES
    assert opsn["M-OPSN-1"].ids_candidats == ["M-DAJ-1"]
    assert daj["M-DAJ-1"].statut is Statut.PRESENT_DEUX_COTES

    # Groupement partiel : un seul titulaire commun suffit
    assert opsn["M-OPSN-2"].statut is Statut.PRESENT_DEUX_COTES
    assert opsn["M-OPSN-2"].ids_candidats == ["M-DAJ-2"]

    # Absent côté DAJ
    assert opsn["M-OPSN-3"].statut is Statut.SEULEMENT_OPSN

    # Absent côté OPSN
    assert daj["M-DAJ-4"].statut is Statut.SEULEMENT_DAJ

    # Ambigu : deux candidats DAJ pour un marché OPSN
    assert opsn["M-OPSN-5"].statut is Statut.PRESENT_DEUX_COTES
    assert opsn["M-OPSN-5"].ambigu is True
    assert set(opsn["M-OPSN-5"].ids_candidats) == {"M-DAJ-5A", "M-DAJ-5B"}
    assert daj["M-DAJ-5A"].statut is Statut.PRESENT_DEUX_COTES
    assert daj["M-DAJ-5A"].ambigu is False

    # Incomparable : dateNotification absente
    assert opsn["M-OPSN-6"].statut is Statut.INCOMPARABLE
    assert opsn["M-OPSN-6"].raison_incomparable == "dateNotification absente"


def test_fichier_racine_invalide():
    marches, stats = extraire_marches(FICHIERS / "invalide", Source.DAJ, SIRETS)

    assert marches == []
    assert stats.fichiers_en_erreur == 1
    assert stats.fichiers_lus == 0


def test_ancien_format_incomparable_et_avertissement(caplog):
    with caplog.at_level(logging.WARNING, logger="rich"):
        marches, _ = extraire_marches(FICHIERS / "ancien", Source.OPSN, SIRETS)

    marche = _par_id(marches)["M-ANCIEN-1"]
    assert marche.statut is Statut.INCOMPARABLE
    assert marche.raison_incomparable.startswith("validation : titulaires")
    assert "ancien format" in caplog.text


def test_dossier_sans_json(tmp_path):
    with pytest.raises(typer.BadParameter, match="Aucun fichier .json"):
        extraire_marches(tmp_path, Source.DAJ, SIRETS)


def test_lire_sirets(tmp_path, caplog):
    fichier = tmp_path / "sirets.txt"
    fichier.write_text("11111111111111\n\n  33333333333333  \npas-un-siret\n")

    with caplog.at_level(logging.WARNING, logger="rich"):
        sirets = lire_sirets(fichier)

    assert sirets == {"11111111111111", "33333333333333", "pas-un-siret"}
    assert "SIRET suspect" in caplog.text


def test_ecrire_csv(tmp_path):
    chemin = tmp_path / "rapport.csv"
    marches = [
        MarcheCompare(
            source=Source.OPSN,
            fichier="megalis.json",
            id_marche="M-1",
            acheteur_id="11111111111111",
            date_notification=date(2023, 1, 1),
            titulaires_ids=frozenset({"22222222222222"}),
            statut=Statut.PRESENT_DEUX_COTES,
            ambigu=True,
            ids_candidats=["M-DAJ-1", "M-DAJ-2"],
        )
    ]

    ecrire_csv(chemin, marches)

    with chemin.open(encoding="utf-8-sig") as f:
        lignes = list(csv.reader(f, delimiter=";"))
    assert lignes[0][0] == "source"
    assert lignes[1] == [
        "opsn",
        "megalis.json",
        "M-1",
        "11111111111111",
        "2023-01-01",
        "22222222222222",
        "present_deux_cotes",
        "oui",
        "M-DAJ-1,M-DAJ-2",
        "",
    ]


def test_cli_comparer(tmp_path):
    fichier_sirets = tmp_path / "sirets.txt"
    fichier_sirets.write_text("11111111111111\n33333333333333\n")
    sortie = tmp_path / "rapport.csv"

    resultat = CliRunner().invoke(
        app,
        [
            "comparer",
            "--dossier-daj",
            str(FICHIERS / "daj"),
            "--dossier-opsn",
            str(FICHIERS / "opsn"),
            "--sirets",
            str(fichier_sirets),
            "--sortie",
            str(sortie),
        ],
    )

    assert resultat.exit_code == 0, resultat.output
    with sortie.open(encoding="utf-8-sig") as f:
        lignes = list(csv.reader(f, delimiter=";"))
    assert len(lignes) == 1 + 6 + 5  # entête + marchés daj + marchés opsn
