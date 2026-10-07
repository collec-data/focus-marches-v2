import os
import sys

from app.helpers.timezone import TZ_EUROPE_PARIS

sys.path.append(os.getcwd())

import csv
import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Any, BinaryIO

import ijson
import requests
import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

app = typer.Typer()

logging.basicConfig(
    level="INFO", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)
log = logging.getLogger("rich")

console = Console()

URL_DATASET = "https://www.data.gouv.fr/api/1/datasets/{slug}/"
# Les URLs static.data.gouv.fr sont versionnées et disparaissent : seule cette
# route par identifiant de ressource est stable dans le temps.
URL_RESSOURCE = "https://www.data.gouv.fr/api/1/datasets/r/{identifiant}"

SLUG_DAJ = "donnees-essentielles-de-la-commande-publique-fichiers-consolides"
SLUG_OPSN = (
    "donnees-essentielles-du-profil-acheteur-megalis-bretagne-schema-arretes-2022"
)

# Les fichiers annuels du consolidé national ne partitionnent ni par date de
# notification ni par date de publication : seul le global est exploitable.
FICHIER_DAJ = "decp-global.json"

DATE_MINIMALE = date(2000, 1, 1)
TOLERANCE_CANDIDAT_JOURS = 60
NB_ACHETEURS_AFFICHES = 20


class Source(StrEnum):
    DAJ = "daj"
    OPSN = "opsn"


class Perimetre(StrEnum):
    MEGALIS = "megalis"
    DAJ_SEUL = "daj_seul"
    ANOMALIE = "anomalie"


class Niveau(StrEnum):
    ID = "id"
    HEURISTIQUE = "heuristique"


class FluxSansNaN:
    """Flux binaire qui remplace les littéraux `NaN` par `null` à la volée.

    Le consolidé national en contient, et le parseur JSON les refuse. Le
    remplacement se fait par blocs, en conservant deux octets d'un bloc au
    suivant pour ne pas manquer un `NaN` à cheval.
    """

    TAILLE_BLOC = 1 << 16

    def __init__(self, fichier: BinaryIO) -> None:
        self._fichier = fichier
        self._pret = b""
        self._report = b""
        self._epuise = False

    def _remplir(self) -> None:
        bloc = self._fichier.read(self.TAILLE_BLOC)
        if not bloc:
            self._pret += self._report.replace(b"NaN", b"null")
            self._report = b""
            self._epuise = True
            return
        donnees = self._report + bloc
        self._report = donnees[-2:]
        self._pret += donnees[:-2].replace(b"NaN", b"null")

    def read(self, taille: int = -1) -> bytes:
        while not self._epuise and (taille < 0 or len(self._pret) < taille):
            self._remplir()
        if taille < 0:
            sortie, self._pret = self._pret, b""
        else:
            sortie, self._pret = self._pret[:taille], self._pret[taille:]
        return sortie


@dataclass
class Ressource:
    titre: str
    identifiant: str
    derniere_maj: str

    @property
    def nom_cache(self) -> str:
        return f"{self.derniere_maj}-{self.titre}"


@dataclass
class Marche:
    source: Source
    fichier: str
    id_marche: str
    acheteur_id: str
    date_notification: date | None
    titulaires_ids: frozenset[str]
    montant: Decimal | None
    anomalie: str = ""
    occurrences: int = 1

    @property
    def cle_id(self) -> tuple[str, str]:
        return (self.acheteur_id, self.id_marche)


@dataclass
class StatistiquesLecture:
    fichiers_lus: int = 0
    fichiers_en_erreur: int = 0
    marches_lus: int = 0
    marches_hors_perimetre: int = 0
    marches_sans_acheteur: int = 0
    marches_en_anomalie: int = 0
    doublons: int = 0


@dataclass
class Rapprochement:
    perimetre: Perimetre
    opsn: Marche | None = None
    daj: Marche | None = None
    niveau: Niveau | None = None
    ambigu: bool = False
    candidat_proche: str = ""
    raison_candidat: str = ""

    @property
    def ecart_date_jours(self) -> int | None:
        if self.opsn is None or self.daj is None:
            return None
        if self.opsn.date_notification is None or self.daj.date_notification is None:
            return None
        return (self.daj.date_notification - self.opsn.date_notification).days

    @property
    def ecart_titulaires(self) -> bool:
        if self.opsn is None or self.daj is None:
            return False
        if not self.opsn.titulaires_ids or not self.daj.titulaires_ids:
            return False
        return not (self.opsn.titulaires_ids & self.daj.titulaires_ids)

    @property
    def ecart_montant(self) -> Decimal | None:
        if self.opsn is None or self.daj is None:
            return None
        if self.opsn.montant is None or self.daj.montant is None:
            return None
        return self.daj.montant - self.opsn.montant

    @property
    def a_un_ecart(self) -> bool:
        return bool(
            self.ecart_date_jours or self.ecart_titulaires or self.ecart_montant
        )


def lister_ressources(slug: str) -> list[Ressource]:
    """Interroge l'API data.gouv et retourne les ressources JSON du jeu."""
    reponse = requests.get(URL_DATASET.format(slug=slug), timeout=120)
    reponse.raise_for_status()
    ressources: list[Ressource] = []
    for brut in reponse.json().get("resources", []):
        if (brut.get("format") or "").lower() != "json":
            continue
        horodatage = str(brut.get("last_modified") or brut.get("created_at") or "")
        ressources.append(
            Ressource(
                titre=str(brut.get("title") or ""),
                identifiant=str(brut.get("id") or ""),
                derniere_maj=horodatage[:10].replace("-", "") or "sansdate",
            )
        )
    return ressources


def telecharger(ressource: Ressource, cache: Path, rafraichir: bool) -> Path:
    """Télécharge la ressource dans le cache, ou réutilise la copie locale.

    Le nom de cache porte la date de mise à jour data.gouv : une version plus
    récente produit un nom différent, les versions périmées sont supprimées.
    """
    cache.mkdir(parents=True, exist_ok=True)
    chemin = cache / ressource.nom_cache
    if chemin.exists() and not rafraichir:
        log.info(f"♻️ Cache : {chemin.name}")
        return chemin

    log.info(f"🌐 Téléchargement de {ressource.titre}")
    partiel = chemin.with_suffix(chemin.suffix + ".partiel")
    reponse = requests.get(
        URL_RESSOURCE.format(identifiant=ressource.identifiant),
        stream=True,
        timeout=(30, 600),
    )
    reponse.raise_for_status()
    with partiel.open("wb") as sortie:
        for bloc in reponse.iter_content(1 << 20):
            sortie.write(bloc)
    partiel.replace(chemin)

    for perime in cache.glob(f"*-{ressource.titre}"):
        if perime != chemin:
            log.info(f"🧹 Version périmée supprimée : {perime.name}")
            perime.unlink()
    return chemin


def telecharger_sources(
    annee: int, cache: Path, rafraichir: bool
) -> tuple[Path, list[Path]]:
    """Retourne le consolidé national et tous les fichiers annuels de l'OPSN.

    Les fichiers annuels de l'OPSN ne sont pas partitionnés par date de
    notification : ils sont tous lus, sans quoi une partie des marchés de
    l'année comparée serait absente du périmètre.
    """
    ressources_daj = lister_ressources(SLUG_DAJ)
    global_daj = next(
        (r for r in ressources_daj if r.titre == FICHIER_DAJ),
        None,
    )
    if global_daj is None:
        raise typer.BadParameter(
            f"Ressource « {FICHIER_DAJ} » introuvable dans le jeu de données DAJ"
        )
    chemin_daj = telecharger(global_daj, cache, rafraichir)

    ressources_opsn = [
        r for r in lister_ressources(SLUG_OPSN) if r.titre.startswith("decp-")
    ]
    if not ressources_opsn:
        raise typer.BadParameter("Aucun fichier decp-*.json dans le jeu de l'OPSN")
    chemins_opsn = [
        telecharger(ressource, cache, rafraichir)
        for ressource in sorted(ressources_opsn, key=lambda r: r.titre)
    ]
    return chemin_daj, chemins_opsn


def _lire_date(valeur: Any) -> tuple[date | None, str]:
    """Retourne la date de notification et, le cas échéant, son anomalie."""
    if valeur in (None, ""):
        return None, "dateNotification absente"
    try:
        lue = date.fromisoformat(str(valeur)[:10])
    except ValueError:
        return None, f"dateNotification illisible : « {valeur} »"
    if lue < DATE_MINIMALE:
        return lue, f"dateNotification antérieure à {DATE_MINIMALE.year} : {lue}"
    if lue > datetime.now(tz=TZ_EUROPE_PARIS).date():
        return lue, f"dateNotification dans le futur : {lue}"
    return lue, ""


def _lire_montant(valeur: Any) -> Decimal | None:
    if valeur in (None, ""):
        return None
    try:
        return round(Decimal(str(valeur)), 2)
    except InvalidOperation, ValueError:
        return None


def _lire_titulaires(valeur: Any) -> frozenset[str]:
    if not isinstance(valeur, list):
        return frozenset()
    identifiants: set[str] = set()
    for enveloppe in valeur:
        if not isinstance(enveloppe, dict):
            continue
        for titulaire in enveloppe.values():
            if isinstance(titulaire, dict) and titulaire.get("id"):
                identifiants.add(str(titulaire["id"]).strip())
    return frozenset(identifiants)


def _construire(objet: dict[str, Any], source: Source, fichier: str) -> Marche | None:
    acheteur = objet.get("acheteur")
    acheteur_id = acheteur.get("id") if isinstance(acheteur, dict) else None
    if not acheteur_id:
        return None
    date_notification, anomalie = _lire_date(objet.get("dateNotification"))
    return Marche(
        source=source,
        fichier=fichier,
        id_marche=str(objet.get("id") or "").strip(),
        acheteur_id=str(acheteur_id).strip(),
        date_notification=date_notification,
        titulaires_ids=_lire_titulaires(objet.get("titulaires")),
        montant=_lire_montant(objet.get("montant")),
        anomalie=anomalie,
    )


def extraire_marches(
    fichiers: list[Path],
    source: Source,
    acheteurs: set[str] | None = None,
) -> tuple[list[Marche], StatistiquesLecture]:
    """Lit les marchés des fichiers, en flux, sans filtre d'année.

    Le filtre d'année est appliqué plus tard : un marché peut porter une date
    de notification différente d'une source à l'autre, et l'appariement doit
    pouvoir le retrouver malgré cet écart.
    """
    marches: list[Marche] = []
    stats = StatistiquesLecture()

    for fichier in fichiers:
        stats.fichiers_lus += 1
        lus_avant = stats.marches_lus
        try:
            with fichier.open("rb") as brut:
                flux = FluxSansNaN(brut)
                for objet in ijson.items(flux, "marches.marche.item"):
                    stats.marches_lus += 1
                    if not isinstance(objet, dict):
                        stats.marches_sans_acheteur += 1
                        continue
                    marche = _construire(objet, source, fichier.name)
                    if marche is None:
                        stats.marches_sans_acheteur += 1
                        continue
                    if acheteurs is not None and marche.acheteur_id not in acheteurs:
                        stats.marches_hors_perimetre += 1
                        continue
                    if marche.anomalie:
                        stats.marches_en_anomalie += 1
                    marches.append(marche)
        except ijson.JSONError as erreur:
            log.error(f"❌ {fichier} : JSON invalide ({erreur}) — lecture interrompue")
            stats.fichiers_en_erreur += 1
            continue

        if stats.marches_lus == lus_avant:
            log.warning(
                f"⚠️ {fichier} : aucun marché sous « marches.marche » — "
                "fichier vide ou format inattendu ?"
            )

    return marches, stats


def dedoublonner(marches: list[Marche], stats: StatistiquesLecture) -> list[Marche]:
    """Fusionne les marchés partageant la clé (acheteur, id).

    Le consolidé national agrège une dizaine de producteurs et republie
    certains marchés plusieurs fois ; le nombre d'occurrences est conservé.
    """
    uniques: dict[tuple[str, str], Marche] = {}
    for marche in marches:
        existant = uniques.get(marche.cle_id)
        if existant is None:
            uniques[marche.cle_id] = marche
        else:
            existant.occurrences += 1
            stats.doublons += 1
    return list(uniques.values())


def apparier(
    marches_opsn: list[Marche], marches_daj: list[Marche]
) -> list[Rapprochement]:
    """Apparie les deux sources : clé (acheteur, id) puis heuristique.

    L'heuristique reprend celle du script de comparaison existant : même
    acheteur, même date de notification et au moins un titulaire commun.
    """
    index_id: dict[tuple[str, str], Marche] = {m.cle_id: m for m in marches_daj}
    index_cle: dict[tuple[str, date], list[Marche]] = defaultdict(list)
    for marche in marches_daj:
        if marche.date_notification is not None:
            index_cle[(marche.acheteur_id, marche.date_notification)].append(marche)

    apparies: set[int] = set()
    rapprochements: list[Rapprochement] = []

    for marche in sorted(marches_opsn, key=lambda m: (m.acheteur_id, m.id_marche)):
        perimetre = Perimetre.ANOMALIE if marche.anomalie else Perimetre.MEGALIS
        rapprochement = Rapprochement(perimetre=perimetre, opsn=marche)

        candidat = index_id.get(marche.cle_id) if marche.id_marche else None
        if candidat is not None and id(candidat) not in apparies:
            rapprochement.daj = candidat
            rapprochement.niveau = Niveau.ID
            apparies.add(id(candidat))
        elif marche.date_notification is not None and marche.titulaires_ids:
            possibles = [
                autre
                for autre in index_cle.get(
                    (marche.acheteur_id, marche.date_notification), []
                )
                if autre.titulaires_ids & marche.titulaires_ids
            ]
            libres = [autre for autre in possibles if id(autre) not in apparies]
            if libres:
                retenu = min(libres, key=lambda m: m.id_marche)
                rapprochement.daj = retenu
                rapprochement.niveau = Niveau.HEURISTIQUE
                rapprochement.ambigu = len(possibles) > 1
                apparies.add(id(retenu))

        rapprochements.append(rapprochement)

    for marche in marches_daj:
        if id(marche) not in apparies:
            rapprochements.append(
                Rapprochement(perimetre=Perimetre.DAJ_SEUL, daj=marche)
            )
    return rapprochements


def chercher_candidats_proches(rapprochements: list[Rapprochement]) -> None:
    """Cherche, pour les marchés OPSN non appariés, un quasi-candidat DAJ.

    Deux passes : montant identique à l'euro près (signature forte), puis
    titulaire commun avec un écart de date toléré. Distingue un marché que le
    national n'a jamais reçu d'un marché présent que l'appariement a raté.
    """
    libres = [
        rapprochement.daj
        for rapprochement in rapprochements
        if rapprochement.perimetre is Perimetre.DAJ_SEUL
        and rapprochement.daj is not None
    ]
    par_montant: dict[tuple[str, Decimal], list[Marche]] = defaultdict(list)
    par_titulaire: dict[tuple[str, str], list[Marche]] = defaultdict(list)
    for marche in libres:
        # Un montant nul ne signe rien : deux marchés à 0 € se ressemblent tous.
        if marche.montant:
            par_montant[(marche.acheteur_id, marche.montant)].append(marche)
        for titulaire in marche.titulaires_ids:
            par_titulaire[(marche.acheteur_id, titulaire)].append(marche)

    for rapprochement in rapprochements:
        cherche = rapprochement.opsn
        if rapprochement.daj is not None or cherche is None:
            continue

        if cherche.montant:
            trouves = par_montant.get((cherche.acheteur_id, cherche.montant), [])
            if trouves:
                rapprochement.candidat_proche = trouves[0].id_marche
                rapprochement.raison_candidat = "montant identique"
                continue

        if cherche.date_notification is None:
            continue
        for titulaire in sorted(cherche.titulaires_ids):
            for autre in par_titulaire.get((cherche.acheteur_id, titulaire), []):
                if autre.date_notification is None:
                    continue
                ecart = abs((autre.date_notification - cherche.date_notification).days)
                if ecart <= TOLERANCE_CANDIDAT_JOURS:
                    rapprochement.candidat_proche = autre.id_marche
                    rapprochement.raison_candidat = f"titulaire commun, écart {ecart} j"
                    break
            if rapprochement.candidat_proche:
                break


def _concerne_annee(rapprochement: Rapprochement, annee: int) -> bool:
    """Un rapprochement entre dans le rapport de l'année s'il porte dessus.

    Les marchés OPSN dont la date est inutilisable sont conservés : ils sont
    signalés comme anomalies plutôt que d'être écartés silencieusement.
    """
    if rapprochement.perimetre is Perimetre.ANOMALIE:
        return True
    marche = rapprochement.opsn or rapprochement.daj
    if marche is None or marche.date_notification is None:
        return False
    return marche.date_notification.year == annee


def _rang_tri(rapprochement: Rapprochement) -> tuple[int, str, str]:
    if rapprochement.perimetre is Perimetre.ANOMALIE:
        rang = 3
    elif rapprochement.perimetre is Perimetre.DAJ_SEUL:
        rang = 4
    elif rapprochement.daj is None:
        rang = 0
    elif rapprochement.a_un_ecart:
        rang = 1
    else:
        rang = 2
    marche = rapprochement.opsn or rapprochement.daj
    return (
        rang,
        marche.acheteur_id if marche else "",
        marche.id_marche if marche else "",
    )


COLONNES = [
    "perimetre",
    "cle",
    "acheteur",
    "id_opsn",
    "id_daj",
    "dans_opsn",
    "dans_daj",
    "niveau",
    "ambigu",
    "date_notification_opsn",
    "date_notification_daj",
    "ecart_date_jours",
    "titulaires_opsn",
    "titulaires_daj",
    "ecart_titulaires",
    "montant_opsn",
    "montant_daj",
    "ecart_montant",
    "nb_occurrences_daj",
    "candidat_proche",
    "raison_candidat",
    "anomalie",
    "fichier_opsn",
    "fichier_daj",
]


def _oui_non(valeur: bool) -> str:
    return "oui" if valeur else "non"


def _texte(valeur: Any) -> str:
    return "" if valeur is None else str(valeur)


def ecrire_csv(chemin: Path, rapprochements: list[Rapprochement]) -> None:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with chemin.open("w", newline="", encoding="utf-8-sig") as fichier:
        writer = csv.writer(fichier, delimiter=";")
        writer.writerow(COLONNES)
        for numero, rapprochement in enumerate(rapprochements, start=1):
            opsn, daj = rapprochement.opsn, rapprochement.daj
            marche = opsn or daj
            writer.writerow(
                [
                    rapprochement.perimetre.value,
                    f"K-{numero:05d}",
                    marche.acheteur_id if marche else "",
                    opsn.id_marche if opsn else "",
                    daj.id_marche if daj else "",
                    _oui_non(opsn is not None),
                    _oui_non(daj is not None),
                    rapprochement.niveau.value if rapprochement.niveau else "",
                    _oui_non(rapprochement.ambigu),
                    _texte(opsn.date_notification if opsn else None),
                    _texte(daj.date_notification if daj else None),
                    _texte(rapprochement.ecart_date_jours),
                    ",".join(sorted(opsn.titulaires_ids)) if opsn else "",
                    ",".join(sorted(daj.titulaires_ids)) if daj else "",
                    _oui_non(rapprochement.ecart_titulaires),
                    _texte(opsn.montant if opsn else None),
                    _texte(daj.montant if daj else None),
                    _texte(rapprochement.ecart_montant),
                    daj.occurrences if daj else "",
                    rapprochement.candidat_proche,
                    rapprochement.raison_candidat,
                    opsn.anomalie if opsn else "",
                    opsn.fichier if opsn else "",
                    daj.fichier if daj else "",
                ]
            )


@dataclass
class LigneSynthese:
    acheteur: str
    nb_opsn: int = 0
    nb_retrouves: int = 0
    nb_ecarts: int = 0
    nb_candidats: int = 0
    nb_daj_seul: int = 0
    nb_doublons_daj: int = 0
    nb_anomalies: int = 0

    @property
    def taux_couverture(self) -> Decimal:
        if not self.nb_opsn:
            return Decimal(0)
        return round(Decimal(self.nb_retrouves) * 100 / self.nb_opsn, 1)


def construire_synthese(
    rapprochements: list[Rapprochement],
) -> list[LigneSynthese]:
    lignes: dict[str, LigneSynthese] = {}
    for rapprochement in rapprochements:
        marche = rapprochement.opsn or rapprochement.daj
        if marche is None:
            continue
        ligne = lignes.setdefault(
            marche.acheteur_id, LigneSynthese(acheteur=marche.acheteur_id)
        )
        if rapprochement.perimetre is Perimetre.DAJ_SEUL:
            ligne.nb_daj_seul += 1
        elif rapprochement.perimetre is Perimetre.ANOMALIE:
            # Une date inutilisable interdit de rattacher le marché à l'année :
            # il est signalé, mais reste hors du taux de couverture.
            ligne.nb_anomalies += 1
        else:
            ligne.nb_opsn += 1
            if rapprochement.daj is not None:
                ligne.nb_retrouves += 1
                if rapprochement.a_un_ecart:
                    ligne.nb_ecarts += 1
            elif rapprochement.candidat_proche:
                ligne.nb_candidats += 1
        if rapprochement.daj is not None:
            ligne.nb_doublons_daj += rapprochement.daj.occurrences - 1
    return sorted(lignes.values(), key=lambda ligne: ligne.acheteur)


def ecrire_synthese(chemin: Path, lignes: list[LigneSynthese]) -> None:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with chemin.open("w", newline="", encoding="utf-8-sig") as fichier:
        writer = csv.writer(fichier, delimiter=";")
        writer.writerow(
            [
                "acheteur",
                "nb_marches_opsn",
                "nb_retrouves",
                "taux_couverture",
                "nb_ecarts",
                "nb_candidats_proches",
                "nb_daj_seul",
                "nb_doublons_daj",
                "nb_anomalies",
            ]
        )
        for ligne in lignes:
            writer.writerow(
                [
                    ligne.acheteur,
                    ligne.nb_opsn,
                    ligne.nb_retrouves,
                    ligne.taux_couverture,
                    ligne.nb_ecarts,
                    ligne.nb_candidats,
                    ligne.nb_daj_seul,
                    ligne.nb_doublons_daj,
                    ligne.nb_anomalies,
                ]
            )


def afficher_resume(
    annee: int,
    rapprochements: list[Rapprochement],
    lignes: list[LigneSynthese],
    stats_opsn: StatistiquesLecture,
    stats_daj: StatistiquesLecture,
) -> None:
    du_perimetre = [r for r in rapprochements if r.perimetre is Perimetre.MEGALIS]
    retrouves = [r for r in du_perimetre if r.daj is not None]
    manquants = [r for r in du_perimetre if r.daj is None]

    table = Table(title=f"Couverture du profil acheteur par le national — {annee}")
    table.add_column("Indicateur")
    table.add_column("Nombre", justify="right")
    table.add_column("Part", justify="right")

    total = len(du_perimetre)

    def part(valeur: int) -> str:
        return f"{100 * valeur / total:.1f} %" if total else "—"

    table.add_row("Marchés OPSN de l'année", str(total), part(total))
    table.add_row(
        "Retrouvés dans le national", str(len(retrouves)), part(len(retrouves))
    )
    for niveau in Niveau:
        nombre = sum(1 for r in retrouves if r.niveau is niveau)
        table.add_row(f"  dont par {niveau.value}", str(nombre), part(nombre))
    table.add_row("Absents du national", str(len(manquants)), part(len(manquants)))
    avec_candidat = sum(1 for r in manquants if r.candidat_proche)
    table.add_row(
        "  dont candidat proche trouvé", str(avec_candidat), part(avec_candidat)
    )
    table.add_section()
    ecarts_date = sum(1 for r in retrouves if r.ecart_date_jours)
    ecarts_titulaires = sum(1 for r in retrouves if r.ecart_titulaires)
    ecarts_montant = sum(1 for r in retrouves if r.ecart_montant)
    table.add_row("Appariés, date divergente", str(ecarts_date), part(ecarts_date))
    table.add_row(
        "Appariés, aucun titulaire commun",
        str(ecarts_titulaires),
        part(ecarts_titulaires),
    )
    table.add_row(
        "Appariés, montant divergent", str(ecarts_montant), part(ecarts_montant)
    )
    table.add_section()
    anomalies = sum(1 for r in rapprochements if r.perimetre is Perimetre.ANOMALIE)
    daj_seul = sum(1 for r in rapprochements if r.perimetre is Perimetre.DAJ_SEUL)
    table.add_row("Marchés OPSN en anomalie de date", str(anomalies), part(anomalies))
    table.add_row("Marchés du national sans contrepartie", str(daj_seul), "—")
    table.add_row("Lignes dupliquées dans le national", str(stats_daj.doublons), "—")
    console.print(table)

    incomplets = [
        ligne
        for ligne in lignes
        if ligne.nb_opsn and ligne.nb_retrouves < ligne.nb_opsn
    ]
    if incomplets:
        pires = sorted(
            incomplets, key=lambda ligne: (ligne.taux_couverture, -ligne.nb_opsn)
        )
        table_acheteurs = Table(
            title=f"Acheteurs les moins bien remontés ({NB_ACHETEURS_AFFICHES} premiers sur {len(incomplets)})"
        )
        table_acheteurs.add_column("Acheteur (SIRET)")
        table_acheteurs.add_column("Marchés OPSN", justify="right")
        table_acheteurs.add_column("Retrouvés", justify="right")
        table_acheteurs.add_column("Couverture", justify="right")
        for ligne in pires[:NB_ACHETEURS_AFFICHES]:
            table_acheteurs.add_row(
                ligne.acheteur,
                str(ligne.nb_opsn),
                str(ligne.nb_retrouves),
                f"{ligne.taux_couverture} %",
            )
        console.print(table_acheteurs)

    for source, stats in ((Source.OPSN, stats_opsn), (Source.DAJ, stats_daj)):
        log.info(
            f"📂 {source.value} : {stats.fichiers_lus} fichier(s) lu(s), "
            f"{stats.fichiers_en_erreur} en erreur, {stats.marches_lus} marché(s) lu(s), "
            f"{stats.marches_hors_perimetre} hors périmètre acheteur, "
            f"{stats.marches_sans_acheteur} sans acheteur exploitable, "
            f"{stats.doublons} doublon(s) fusionné(s)"
        )


def comparer_annee(
    annee: int,
    chemin_daj: Path,
    chemins_opsn: list[Path],
) -> tuple[
    list[Rapprochement], list[LigneSynthese], StatistiquesLecture, StatistiquesLecture
]:
    """Enchaîne lecture, déduplication, appariement et filtrage sur l'année."""
    log.info(f"📖 Lecture de l'OPSN : {len(chemins_opsn)} fichier(s)")
    marches_opsn, stats_opsn = extraire_marches(chemins_opsn, Source.OPSN)
    marches_opsn = dedoublonner(marches_opsn, stats_opsn)
    if not marches_opsn:
        raise typer.BadParameter("Aucun marché exploitable dans les fichiers de l'OPSN")

    acheteurs = {marche.acheteur_id for marche in marches_opsn}
    log.info(f"🔍 Périmètre : {len(acheteurs)} acheteur(s) issus de l'OPSN")

    log.info(f"📖 Lecture du consolidé national : {chemin_daj.name}")
    marches_daj, stats_daj = extraire_marches([chemin_daj], Source.DAJ, acheteurs)
    marches_daj = dedoublonner(marches_daj, stats_daj)

    log.info("🔗 Appariement (clé identifiant, puis heuristique)")
    rapprochements = apparier(marches_opsn, marches_daj)
    chercher_candidats_proches(rapprochements)

    retenus = [r for r in rapprochements if _concerne_annee(r, annee)]
    retenus.sort(key=_rang_tri)
    return retenus, construire_synthese(retenus), stats_opsn, stats_daj


@app.callback()
def principal() -> None:
    """Comparaison annuelle entre le consolidé national et un profil acheteur."""


@app.command()
def comparer(
    annee: Annotated[
        int,
        typer.Option(help="Année de notification à comparer"),
    ],
    cache: Annotated[
        Path,
        typer.Option(help="Dossier de cache des fichiers téléchargés"),
    ] = Path("./decp-cache"),
    sortie: Annotated[Path, typer.Option(help="Dossier des rapports produits")] = Path(
        "./rapports"
    ),
    rafraichir: Annotated[
        bool,
        typer.Option(help="Force le retéléchargement même si le cache est à jour"),
    ] = False,
) -> None:
    """Vérifie que les marchés du profil acheteur figurent dans le national."""
    if not 2000 <= annee <= datetime.now(tz=TZ_EUROPE_PARIS).year + 1:
        raise typer.BadParameter(f"Année hors bornes : {annee}")

    chemin_daj, chemins_opsn = telecharger_sources(annee, cache, rafraichir)
    rapprochements, lignes, stats_opsn, stats_daj = comparer_annee(
        annee, chemin_daj, chemins_opsn
    )

    fichier_rapport = sortie / f"comparaison-{annee}.csv"
    fichier_synthese = sortie / f"synthese-{annee}.csv"
    ecrire_csv(fichier_rapport, rapprochements)
    ecrire_synthese(fichier_synthese, lignes)
    log.info(f"💾 Rapport écrit : {fichier_rapport} ({len(rapprochements)} ligne(s))")
    log.info(f"💾 Synthèse écrite : {fichier_synthese} ({len(lignes)} acheteur(s))")

    afficher_resume(annee, rapprochements, lignes, stats_opsn, stats_daj)


if __name__ == "__main__":
    app()
