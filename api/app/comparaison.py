import os
import sys

sys.path.append(os.getcwd())

import csv
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum
from pathlib import Path
from typing import Any

import ijson
import typer
from pydantic import BaseModel
from pydantic_core import ValidationError
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

from app.models.dto_importation import AcheteurSchema, TitulaireSchema

app = typer.Typer()

logging.basicConfig(
    level="INFO", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)
log = logging.getLogger("rich")

console = Console()


class Source(StrEnum):
    DAJ = "daj"
    OPSN = "opsn"


class Statut(StrEnum):
    PRESENT_DEUX_COTES = "present_deux_cotes"
    SEULEMENT_DAJ = "seulement_daj"
    SEULEMENT_OPSN = "seulement_opsn"
    INCOMPARABLE = "incomparable"


class MarcheCompareSchema(BaseModel):
    """Schéma allégé du format DECP 2022 : seuls les champs utiles à
    l'appariement sont validés, le reste du marché est ignoré."""

    id: str | None = None
    acheteur: AcheteurSchema
    dateNotification: date | None = None
    titulaires: list[dict[str, TitulaireSchema]] | None = None


@dataclass
class MarcheCompare:
    source: Source
    fichier: str
    id_marche: str
    acheteur_id: str
    date_notification: date | None
    titulaires_ids: frozenset[str]
    statut: Statut | None = None
    ambigu: bool = False
    ids_candidats: list[str] = field(default_factory=list)
    raison_incomparable: str = ""


@dataclass
class StatistiquesLecture:
    fichiers_lus: int = 0
    fichiers_en_erreur: int = 0
    marches_lus: int = 0
    marches_hors_filtre: int = 0
    marches_sans_acheteur: int = 0


def lire_sirets(fichier: Path) -> set[str]:
    sirets: set[str] = set()
    for ligne in fichier.read_text(encoding="utf-8").splitlines():
        siret = ligne.strip()
        if not siret:
            continue
        if not (siret.isdigit() and len(siret) == 14):
            log.warning(f"⚠️ SIRET suspect dans {fichier} : « {siret} »")
        sirets.add(siret)
    return sirets


def _contient_cle_marches(fichier: Path) -> bool:
    """Vérifie que la racine du JSON est un objet contenant la clé
    « marches » (structure du schéma 2022). S'arrête à la première clé
    racine trouvée pour ne pas parcourir tout le fichier."""
    with fichier.open("rb") as f:
        try:
            for prefixe, evenement, valeur in ijson.parse(f):
                if prefixe == "" and evenement == "map_key":
                    return bool(valeur == "marches")
                if prefixe == "" and evenement != "start_map":
                    return False  # racine non-objet (ex. tableau, ancien format)
        except ijson.JSONError:
            return False
    return False


def _construire_marche(
    objet: dict[str, Any], source: Source, fichier: Path, acheteur_id: str
) -> MarcheCompare:
    try:
        valide = MarcheCompareSchema(**objet)
    except ValidationError as e:
        premiere = e.errors()[0]
        champ = ".".join(str(loc) for loc in premiere["loc"])
        return MarcheCompare(
            source=source,
            fichier=fichier.name,
            id_marche=str(objet.get("id") or ""),
            acheteur_id=acheteur_id,
            date_notification=None,
            titulaires_ids=frozenset(),
            statut=Statut.INCOMPARABLE,
            raison_incomparable=f"validation : {champ} — {premiere['msg']}",
        )

    titulaires_ids = frozenset(
        titulaire.id
        for enveloppe in (valide.titulaires or [])
        for titulaire in enveloppe.values()
    )
    marche = MarcheCompare(
        source=source,
        fichier=fichier.name,
        id_marche=valide.id or "",
        acheteur_id=acheteur_id,
        date_notification=valide.dateNotification,
        titulaires_ids=titulaires_ids,
    )
    if valide.dateNotification is None:
        marche.statut = Statut.INCOMPARABLE
        marche.raison_incomparable = "dateNotification absente"
    elif not titulaires_ids:
        marche.statut = Statut.INCOMPARABLE
        marche.raison_incomparable = "aucun titulaire"
    return marche


def extraire_marches(
    dossier: Path, source: Source, sirets: set[str]
) -> tuple[list[MarcheCompare], StatistiquesLecture]:
    """Parcourt tous les *.json du dossier et retourne les marchés dont
    l'acheteur est dans la liste de SIRETs, avec les statistiques de lecture."""
    marches: list[MarcheCompare] = []
    stats = StatistiquesLecture()

    fichiers = sorted(dossier.rglob("*.json"))
    if not fichiers:
        raise typer.BadParameter(f"Aucun fichier .json trouvé dans {dossier}")

    for fichier in fichiers:
        if not _contient_cle_marches(fichier):
            log.error(
                f"❌ {fichier} : clé racine « marches » absente ou JSON invalide "
                "(format non conforme au schéma 2022) — fichier ignoré"
            )
            stats.fichiers_en_erreur += 1
            continue

        stats.fichiers_lus += 1
        marches_fichier = 0
        comparables = 0
        incomparables = 0
        with fichier.open("rb") as f:
            try:
                for objet in ijson.items(f, "marches.marche.item"):
                    marches_fichier += 1
                    stats.marches_lus += 1

                    acheteur_id = None
                    if isinstance(objet, dict):
                        acheteur_id = (objet.get("acheteur") or {}).get("id")
                    if not isinstance(acheteur_id, str):
                        stats.marches_sans_acheteur += 1
                        continue
                    if acheteur_id.strip() not in sirets:
                        stats.marches_hors_filtre += 1
                        continue

                    marche = _construire_marche(
                        objet, source, fichier, acheteur_id.strip()
                    )
                    if marche.statut is Statut.INCOMPARABLE:
                        incomparables += 1
                    else:
                        comparables += 1
                    marches.append(marche)
            except ijson.JSONError as e:
                log.error(f"❌ {fichier} : JSON invalide ({e}) — lecture interrompue")
                stats.fichiers_en_erreur += 1
                continue

        if marches_fichier == 0:
            log.warning(
                f"⚠️ {fichier} : aucun marché sous « marches.marche » — "
                "fichier vide ou ancien format DECP ?"
            )
        elif comparables == 0 and incomparables > 0:
            log.warning(
                f"⚠️ {fichier} : tous les marchés filtrés sont invalides — "
                "probablement un fichier à l'ancien format DECP"
            )

    return marches, stats


def apparier(
    marches_daj: list[MarcheCompare], marches_opsn: list[MarcheCompare]
) -> None:
    """Appariement en place : clé (acheteur, dateNotification) + au moins un
    titulaire commun. Les statuts et candidats sont posés sur chaque marché."""
    index_daj: dict[tuple[str, date], list[MarcheCompare]] = defaultdict(list)
    for marche in marches_daj:
        if marche.statut is None and marche.date_notification is not None:
            index_daj[(marche.acheteur_id, marche.date_notification)].append(marche)

    for marche in marches_opsn:
        if marche.statut is not None or marche.date_notification is None:
            continue
        candidats = [
            candidat
            for candidat in index_daj.get(
                (marche.acheteur_id, marche.date_notification), []
            )
            if candidat.titulaires_ids & marche.titulaires_ids
        ]
        if not candidats:
            marche.statut = Statut.SEULEMENT_OPSN
            continue
        marche.statut = Statut.PRESENT_DEUX_COTES
        marche.ambigu = len(candidats) > 1
        marche.ids_candidats = [candidat.id_marche for candidat in candidats]
        for candidat in candidats:
            candidat.statut = Statut.PRESENT_DEUX_COTES
            candidat.ids_candidats.append(marche.id_marche)

    for marche in marches_daj:
        if marche.statut is None:
            marche.statut = Statut.SEULEMENT_DAJ
        elif len(marche.ids_candidats) > 1:
            marche.ambigu = True


def ecrire_csv(chemin: Path, marches: list[MarcheCompare]) -> None:
    with chemin.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(
            [
                "source",
                "fichier",
                "id_marche",
                "acheteur_id",
                "date_notification",
                "titulaires_ids",
                "statut",
                "ambigu",
                "ids_candidats",
                "raison_incomparable",
            ]
        )
        for marche in marches:
            writer.writerow(
                [
                    marche.source.value,
                    marche.fichier,
                    marche.id_marche,
                    marche.acheteur_id,
                    marche.date_notification.isoformat()
                    if marche.date_notification
                    else "",
                    ",".join(sorted(marche.titulaires_ids)),
                    marche.statut.value if marche.statut else "",
                    "oui" if marche.ambigu else "non",
                    ",".join(marche.ids_candidats),
                    marche.raison_incomparable,
                ]
            )


def afficher_resume(
    marches: list[MarcheCompare],
    stats_daj: StatistiquesLecture,
    stats_opsn: StatistiquesLecture,
) -> None:
    table_statuts = Table(title="Marchés par statut")
    table_statuts.add_column("Statut")
    table_statuts.add_column("DAJ", justify="right")
    table_statuts.add_column("OPSN", justify="right")
    for statut in Statut:
        nb_daj = sum(
            1 for m in marches if m.source is Source.DAJ and m.statut is statut
        )
        nb_opsn = sum(
            1 for m in marches if m.source is Source.OPSN and m.statut is statut
        )
        table_statuts.add_row(statut.value, str(nb_daj), str(nb_opsn))
    nb_ambigus = sum(1 for m in marches if m.ambigu)
    table_statuts.add_row("dont ambigus", *_comptes_ambigus(marches))
    console.print(table_statuts)

    table_acheteurs = Table(title="Marchés par acheteur (SIRET)")
    table_acheteurs.add_column("Acheteur")
    for statut in Statut:
        table_acheteurs.add_column(statut.value, justify="right")
    comptes: dict[str, dict[Statut, int]] = defaultdict(lambda: defaultdict(int))
    for marche in marches:
        if marche.statut is not None:
            comptes[marche.acheteur_id][marche.statut] += 1
    for acheteur_id in sorted(comptes):
        table_acheteurs.add_row(
            acheteur_id, *(str(comptes[acheteur_id][statut]) for statut in Statut)
        )
    console.print(table_acheteurs)

    for source, stats in ((Source.DAJ, stats_daj), (Source.OPSN, stats_opsn)):
        log.info(
            f"📂 {source.value} : {stats.fichiers_lus} fichier(s) lu(s), "
            f"{stats.fichiers_en_erreur} en erreur, {stats.marches_lus} marché(s) lu(s), "
            f"{stats.marches_hors_filtre} hors filtre SIRET, "
            f"{stats.marches_sans_acheteur} sans acheteur exploitable"
        )
    if nb_ambigus:
        log.warning(f"⚠️ {nb_ambigus} appariement(s) ambigu(s) à contrôler")


def _comptes_ambigus(marches: list[MarcheCompare]) -> tuple[str, str]:
    return (
        str(sum(1 for m in marches if m.source is Source.DAJ and m.ambigu)),
        str(sum(1 for m in marches if m.source is Source.OPSN and m.ambigu)),
    )


@app.callback()
def principal() -> None:
    """Outils de comparaison de fichiers DECP (schéma 2022)."""


@app.command()
def comparer(
    dossier_daj: Path = typer.Option(
        ..., exists=True, file_okay=False, help="Dossier des fichiers consolidés DAJ"
    ),
    dossier_opsn: Path = typer.Option(
        ..., exists=True, file_okay=False, help="Dossier des fichiers de l'OPSN"
    ),
    sirets: Path = typer.Option(
        ...,
        exists=True,
        dir_okay=False,
        help="Fichier texte des SIRETs acheteurs à considérer (un par ligne)",
    ),
    sortie: Path = typer.Option(
        Path("rapport.csv"), help="Chemin du rapport CSV à produire"
    ),
) -> None:
    """Compare la présence des marchés entre le consolidé DAJ et les fichiers
    d'un OPSN, pour les acheteurs de la liste de SIRETs."""
    liste_sirets = lire_sirets(sirets)
    if not liste_sirets:
        raise typer.BadParameter(f"Aucun SIRET dans {sirets}")
    log.info(f"🔍 {len(liste_sirets)} SIRET(s) acheteur(s) à comparer")

    log.info(f"📖 Lecture du dossier DAJ : {dossier_daj}")
    marches_daj, stats_daj = extraire_marches(dossier_daj, Source.DAJ, liste_sirets)
    log.info(f"📖 Lecture du dossier OPSN : {dossier_opsn}")
    marches_opsn, stats_opsn = extraire_marches(dossier_opsn, Source.OPSN, liste_sirets)

    apparier(marches_daj, marches_opsn)

    marches = marches_daj + marches_opsn
    ecrire_csv(sortie, marches)
    log.info(f"💾 Rapport écrit : {sortie} ({len(marches)} ligne(s))")

    afficher_resume(marches, stats_daj, stats_opsn)


if __name__ == "__main__":
    app()
