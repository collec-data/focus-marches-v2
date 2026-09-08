import csv
import io
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
import typer
from typer.testing import CliRunner

from app.comparaison_annuelle import (
    FluxSansNaN,
    Niveau,
    Perimetre,
    Ressource,
    Source,
    app,
    comparer_annee,
    construire_synthese,
    dedoublonner,
    extraire_marches,
    telecharger,
)

FICHIERS = Path("tests/files/comparaison_annuelle")
DAJ = FICHIERS / "daj" / "decp-global.json"
OPSN = sorted((FICHIERS / "opsn").glob("*.json"))
ACHETEUR_A = "11111111111111"
ACHETEUR_B = "22222222222222"


# La comparaison ne touche pas à la base de données : on neutralise les
# fixtures autouse de conftest.py pour ne pas démarrer le conteneur MariaDB.
@pytest.fixture(scope="module")
def db_url():
    return ""


@pytest.fixture(name="db")
def db_fixture():
    return None


@pytest.fixture(name="rapport")
def rapport_fixture():
    rapprochements, lignes, stats_opsn, stats_daj = comparer_annee(2024, DAJ, OPSN)
    return rapprochements, lignes, stats_opsn, stats_daj


def _par_id_opsn(rapprochements):
    return {r.opsn.id_marche: r for r in rapprochements if r.opsn is not None}


def _par_id_daj(rapprochements):
    return {r.daj.id_marche: r for r in rapprochements if r.daj is not None}


def test_flux_sans_nan_remplace_a_cheval_sur_deux_blocs(monkeypatch):
    monkeypatch.setattr(FluxSansNaN, "TAILLE_BLOC", 8)
    brut = io.BytesIO(b'{"a": NaN, "b": NaN, "c": 1}')

    flux = FluxSansNaN(brut)
    morceaux = []
    while True:
        morceau = flux.read(5)
        if not morceau:
            break
        morceaux.append(morceau)

    assert b"".join(morceaux) == b'{"a": null, "b": null, "c": 1}'


def test_lecture_de_tous_les_fichiers_opsn():
    marches, stats = extraire_marches(OPSN, Source.OPSN)

    assert stats.fichiers_lus == 2
    assert stats.marches_lus == 13
    # Un marché notifié en 2024 est rangé dans le fichier 2023 : lire le seul
    # fichier de l'année en raterait une partie.
    par_id = {m.id_marche: m for m in marches}
    assert par_id["2024T0012"].fichier == "megalis-2023.json"
    assert par_id["2024T0012"].date_notification == date(2024, 10, 12)


def test_lecture_daj_filtre_le_perimetre_acheteur():
    acheteurs = {ACHETEUR_A, ACHETEUR_B}
    marches, stats = extraire_marches([DAJ], Source.DAJ, acheteurs)

    assert stats.marches_lus == 16
    assert stats.marches_hors_perimetre == 1
    assert stats.marches_sans_acheteur == 1
    assert len(marches) == 14
    assert all(m.acheteur_id in acheteurs for m in marches)


def test_montant_nan_lu_sans_erreur():
    marches, _ = extraire_marches([DAJ], Source.DAJ, {ACHETEUR_A})

    par_id = {m.id_marche: m for m in marches}
    assert par_id["DAJ-NAN"].montant is None
    assert par_id["DAJ-S13"].montant == Decimal("1300")


def test_dedoublonnage_compte_les_occurrences():
    marches, stats = extraire_marches([DAJ], Source.DAJ, {ACHETEUR_A, ACHETEUR_B})

    uniques = dedoublonner(marches, stats)

    par_id = {m.id_marche: m for m in uniques}
    assert par_id["2024T0014"].occurrences == 3
    assert stats.doublons == 2
    assert len(uniques) == 12


def test_fichier_json_invalide_signale_et_non_fatal():
    marches, stats = extraire_marches(
        [FICHIERS / "invalide" / "tronque.json"], Source.DAJ
    )

    assert marches == []
    assert stats.fichiers_en_erreur == 1


def test_appariement_par_identifiant(rapport):
    rapprochements, *_ = rapport

    rapprochement = _par_id_opsn(rapprochements)["2024T0001"]
    assert rapprochement.niveau is Niveau.ID
    assert rapprochement.daj is not None
    assert rapprochement.daj.id_marche == "2024T0001"
    assert rapprochement.a_un_ecart is False


def test_appariement_par_heuristique_quand_identifiant_reecrit(rapport):
    rapprochements, *_ = rapport

    rapprochement = _par_id_opsn(rapprochements)["2024T0002"]
    assert rapprochement.niveau is Niveau.HEURISTIQUE
    assert rapprochement.daj is not None
    assert rapprochement.daj.id_marche == "DAJ-X2"


def test_ecarts_sur_marches_apparies(rapport):
    rapprochements, *_ = rapport
    par_id = _par_id_opsn(rapprochements)

    assert par_id["2024T0003"].ecart_date_jours == 17
    assert par_id["2024T0003"].ecart_titulaires is False
    assert par_id["2024T0004"].ecart_titulaires is True
    assert par_id["2024T0004"].ecart_date_jours == 0
    assert par_id["2024T0005"].ecart_montant == Decimal("500")
    assert par_id["2024T0001"].ecart_montant == Decimal("0")


def test_occurrences_du_national_remontees(rapport):
    rapprochements, *_ = rapport

    rapprochement = _par_id_opsn(rapprochements)["2024T0014"]
    assert rapprochement.daj is not None
    assert rapprochement.daj.occurrences == 3


def test_candidat_proche_par_montant(rapport):
    rapprochements, *_ = rapport

    rapprochement = _par_id_opsn(rapprochements)["2024T0006"]
    assert rapprochement.daj is None
    assert rapprochement.candidat_proche == "DAJ-P6"
    assert rapprochement.raison_candidat == "montant identique"


def test_candidat_proche_par_titulaire_et_date(rapport):
    rapprochements, *_ = rapport

    rapprochement = _par_id_opsn(rapprochements)["2024T0007"]
    assert rapprochement.daj is None
    assert rapprochement.candidat_proche == "DAJ-P7"
    assert rapprochement.raison_candidat == "titulaire commun, écart 39 j"


def test_montant_nul_ne_sert_pas_de_candidat():
    from app.comparaison_annuelle import (
        Marche,
        Rapprochement,
        chercher_candidats_proches,
    )

    opsn = Marche(
        source=Source.OPSN,
        fichier="opsn.json",
        id_marche="OPSN-0",
        acheteur_id=ACHETEUR_A,
        date_notification=date(2024, 1, 1),
        titulaires_ids=frozenset({"10000000000031"}),
        montant=Decimal("0.00"),
    )
    daj = Marche(
        source=Source.DAJ,
        fichier="daj.json",
        id_marche="DAJ-0",
        acheteur_id=ACHETEUR_A,
        date_notification=date(2024, 6, 30),
        titulaires_ids=frozenset({"10000000000032"}),
        montant=Decimal("0.00"),
    )
    rapprochements = [
        Rapprochement(perimetre=Perimetre.MEGALIS, opsn=opsn),
        Rapprochement(perimetre=Perimetre.DAJ_SEUL, daj=daj),
    ]

    chercher_candidats_proches(rapprochements)

    assert rapprochements[0].candidat_proche == ""


def test_absent_sans_candidat(rapport):
    rapprochements, *_ = rapport

    rapprochement = _par_id_opsn(rapprochements)["2024T0008"]
    assert rapprochement.daj is None
    assert rapprochement.candidat_proche == ""


def test_anomalie_de_date_conservee_et_appariable(rapport):
    rapprochements, *_ = rapport
    par_id = _par_id_opsn(rapprochements)

    sans_date = par_id["2024T0009"]
    assert sans_date.perimetre is Perimetre.ANOMALIE
    assert sans_date.opsn.anomalie == "dateNotification absente"
    assert sans_date.niveau is Niveau.ID

    futur = par_id["2027T0010"]
    assert futur.perimetre is Perimetre.ANOMALIE
    assert "futur" in futur.opsn.anomalie


def test_filtre_annee(rapport):
    rapprochements, *_ = rapport
    ids_opsn = set(_par_id_opsn(rapprochements))
    ids_daj = set(_par_id_daj(rapprochements))

    assert "2024T0012" in ids_opsn  # notifié en 2024, rangé dans le fichier 2023
    assert "2023T0011" not in ids_opsn
    assert "DAJ-2023" not in ids_daj


def test_marches_du_national_sans_contrepartie(rapport):
    rapprochements, *_ = rapport

    daj_seul = {
        r.daj.id_marche
        for r in rapprochements
        if r.perimetre is Perimetre.DAJ_SEUL and r.daj
    }
    assert daj_seul == {"DAJ-P6", "DAJ-P7", "DAJ-S13", "DAJ-NAN"}


def test_tri_place_les_manquants_en_tete(rapport):
    rapprochements, *_ = rapport

    perimetres = [r.perimetre for r in rapprochements]
    assert perimetres.index(Perimetre.ANOMALIE) < perimetres.index(Perimetre.DAJ_SEUL)
    manquants = [r for r in rapprochements[:3] if r.daj is None]
    assert len(manquants) == 3


def test_synthese_par_acheteur(rapport):
    rapprochements, lignes, *_ = rapport
    par_acheteur = {ligne.acheteur: ligne for ligne in lignes}

    a = par_acheteur[ACHETEUR_A]
    assert a.nb_opsn == 8
    assert a.nb_retrouves == 6
    assert a.nb_ecarts == 3
    assert a.nb_doublons_daj == 2
    assert a.taux_couverture == Decimal("75.0")
    # Les marchés à date inutilisable sont signalés hors du taux de couverture.
    assert a.nb_anomalies == 2

    b = par_acheteur[ACHETEUR_B]
    assert b.nb_opsn == 2
    assert b.nb_retrouves == 0
    assert b.nb_candidats == 2
    assert b.nb_daj_seul == 2


def test_construire_synthese_sans_marche_opsn():
    lignes = construire_synthese([])

    assert lignes == []


def test_cli_ecrit_les_deux_rapports(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "app.comparaison_annuelle.telecharger_sources",
        lambda annee, cache, rafraichir: (DAJ, OPSN),
    )

    resultat = CliRunner().invoke(
        app,
        [
            "comparer",
            "--annee",
            "2024",
            "--sortie",
            str(tmp_path),
            "--cache",
            str(tmp_path / "cache"),
        ],
    )

    assert resultat.exit_code == 0, resultat.output
    with (tmp_path / "comparaison-2024.csv").open(encoding="utf-8-sig") as fichier:
        lignes = list(csv.DictReader(fichier, delimiter=";"))
    assert len(lignes) == 16
    assert lignes[0]["perimetre"] == "megalis"
    assert lignes[0]["dans_daj"] == "non"
    assert lignes[-1]["perimetre"] == "daj_seul"

    par_id = {ligne["id_opsn"]: ligne for ligne in lignes if ligne["id_opsn"]}
    assert par_id["2024T0001"]["niveau"] == "id"
    assert par_id["2024T0002"]["niveau"] == "heuristique"
    assert par_id["2024T0003"]["ecart_date_jours"] == "17"
    assert par_id["2024T0004"]["ecart_titulaires"] == "oui"
    assert par_id["2024T0005"]["ecart_montant"] == "500.00"
    assert par_id["2024T0014"]["nb_occurrences_daj"] == "3"
    assert par_id["2024T0006"]["candidat_proche"] == "DAJ-P6"
    assert par_id["2024T0009"]["perimetre"] == "anomalie"
    assert par_id["2024T0009"]["anomalie"] == "dateNotification absente"

    with (tmp_path / "synthese-2024.csv").open(encoding="utf-8-sig") as fichier:
        synthese = list(csv.DictReader(fichier, delimiter=";"))
    assert {ligne["acheteur"] for ligne in synthese} == {ACHETEUR_A, ACHETEUR_B}
    assert synthese[0]["taux_couverture"] == "75.0"
    assert synthese[0]["nb_anomalies"] == "2"


def test_cli_refuse_une_annee_hors_bornes(tmp_path):
    resultat = CliRunner().invoke(app, ["comparer", "--annee", "1998"])

    assert resultat.exit_code != 0


def test_telecharger_reutilise_le_cache(tmp_path, monkeypatch):
    ressource = Ressource(
        titre="decp-global.json", identifiant="abc", derniere_maj="20260831"
    )
    attendu = tmp_path / "20260831-decp-global.json"
    attendu.write_text("déjà là", encoding="utf-8")

    def refuser(*args, **kwargs):
        raise AssertionError("aucun téléchargement ne doit être déclenché")

    monkeypatch.setattr("app.comparaison_annuelle.requests.get", refuser)

    assert telecharger(ressource, tmp_path, rafraichir=False) == attendu


def test_telecharger_supprime_la_version_perimee(tmp_path, monkeypatch):
    ressource = Ressource(
        titre="decp-global.json", identifiant="abc", derniere_maj="20260901"
    )
    perime = tmp_path / "20260831-decp-global.json"
    perime.write_text("ancienne version", encoding="utf-8")

    class ReponseFactice:
        def raise_for_status(self):
            return None

        def iter_content(self, taille):
            yield b'{"marches": {"marche": []}}'

    monkeypatch.setattr(
        "app.comparaison_annuelle.requests.get",
        lambda *args, **kwargs: ReponseFactice(),
    )

    chemin = telecharger(ressource, tmp_path, rafraichir=False)

    assert chemin == tmp_path / "20260901-decp-global.json"
    assert chemin.exists()
    assert not perime.exists()


def test_comparer_annee_refuse_un_opsn_vide(tmp_path):
    vide = tmp_path / "vide.json"
    vide.write_text('{"marches": {"marche": []}}', encoding="utf-8")

    with pytest.raises(typer.BadParameter, match="Aucun marché exploitable"):
        comparer_annee(2024, DAJ, [vide])
