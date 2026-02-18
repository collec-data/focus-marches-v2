import os
import sys

sys.path.append(os.getcwd())

import csv
import json
import logging
import time
from collections.abc import Callable, Generator
from datetime import date
from decimal import Decimal
from enum import Enum
from functools import cache
from typing import Any

import ijson
import requests
import rich
import rich.progress
import typer
from api_entreprise.exceptions import ApiEntrepriseClientError
from pydantic_core import ValidationError
from rich.logging import RichHandler
from rich.progress import track
from sqlalchemy import desc, select, text
from sqlalchemy.orm import Session

from app.config import get_config
from app.db import get_engine
from app.dependencies import get_api_entreprise
from app.helpers import categorisation
from app.models.db import (
    CPV,
    ActeSousTraitance,
    Base,
    ConsiderationEnvMarche,
    ConsiderationSocialeMarche,
    ContratConcession,
    DecpMalForme,
    DonneeExecution,
    Erreur,
    Lieu,
    Marche,
    ModificationConcession,
    ModificationMarche,
    ModificationSousTraitance,
    Structure,
    StructureInfogreffe,
    Tarif,
    TechniqueAchatMarche,
    concession_structure_table,
    marche_titulaire_table,
    modification_titulaire_table,
)
from app.models.dto_importation import (
    ActeSousTraitanceSchema,
    ConcessionnaireSchema,
    ConcessionSchema,
    DonneeExecutionSchema,
    MarcheAncienSchema,
    MarcheSchema,
    ModificationActeSousTraitanceSchema,
    ModificationConcessionSchema,
    ModificationMarcheSchema,
    TarifSchema,
)
from app.models.enums import TechniqueAchat, TypeCodeLieu

app = typer.Typer()

logging.basicConfig(
    level="INFO", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)
log = logging.getLogger("rich")


class TypeContrat(Enum):
    MARCHE = "marche"
    CONCESSION = "concession"


class CustomValidationError(Exception):
    def __init__(
        self, message: str = "", errors: list[dict[str, str | list[str]]] = []
    ):
        super().__init__(message)
        self._errors = errors

    def errors(self) -> list[dict[str, str | list[str]]]:
        return self._errors


class ImportateurDecp:
    def __init__(self, session: Session, preload_db: bool = True):
        self._cache_lieux: dict[str, Lieu] = {}
        self._cache_structures: dict[str, Structure] = {}
        self._cache_accords_cadre: dict[str, Marche] = {}

        self._session: Session = session

        self._valid_objects: int = 0
        self._invalid_objects: int = 0
        self._started_at: float
        self._finished_at: float

        if preload_db:
            self.load_structures()
            self.load_lieux()
            # pas de chargement des accords cadres car
            # on vide cette table avant chaque ré-import

    def load_structures(self) -> None:
        structures = self._session.execute(select(Structure)).scalars()
        for structure in structures:
            self._cache_structures[
                structure.identifiant + structure.type_identifiant
            ] = structure

    def load_lieux(self) -> None:
        lieux = self._session.execute(select(Lieu)).scalars()
        for lieu in lieux:
            self._cache_lieux[lieu.code + str(lieu.type_code)] = lieu

    def set_acheteur(self, structure: Structure) -> Structure:
        structure.acheteur = True
        return structure

    def set_vendeur(self, structure: Structure) -> Structure:
        structure.vendeur = True
        return structure

    @cache
    def get_or_create_structure(
        self,
        id: str,
        type_id: str = "SIRET",
    ) -> Structure:
        """
        Récupère la structure ou la créé si elle n'existe pas.

        La méthode va, dans l'ordre d'exécution, rechercher dans :
         - son @cache
         - self._cache_structures qui a été chargé depuis la BDD à
           l'initialisation de l'importateur
        Si aucun des cas ci-dessus n'a trouvé la structure, alors on la créé.

        ATTENTION : le cache ne fonctionne qu'en cas d'appel exactement
        identique, passer `1` ou `id=1` en paramètre sera considéré
        comme deux appels différents
        """
        if (id + type_id) in self._cache_structures.keys():
            return self._cache_structures[id + type_id]

        structure = Structure(identifiant=id, type_identifiant=type_id)
        self._session.add(
            structure
        )  # le cascade ne s'applique pas automatiquement en ManyToMany

        return structure

    @cache
    def get_or_create_lieu(self, code: str, type_code: TypeCodeLieu) -> Lieu:
        """
        Récupère le lieu ou le créé si il n'existe pas.

        La méthode va, dans l'ordre d'exécution, rechercher dans :
         - son @cache
         - self._cache_lieux qui a été chargé depuis la BDD à
           l'initialisation de l'importateur
        Si aucun des cas ci-dessus n'a trouvé le lieu, alors on le créé.
        """
        if code + str(type_code.db_value) in self._cache_lieux:
            return self._cache_lieux[code + str(type_code.db_value)]

        return Lieu(
            code=code,
            type_code=type_code.db_value,
        )

    @cache
    def get_accord_cadre(self, id: str) -> Marche | None:
        if id in self._cache_accords_cadre:
            return self._cache_accords_cadre[id]
        return None

    def marche_transformer(
        self,
        objet: dict[str, Any],
    ) -> None:
        data: MarcheSchema | MarcheAncienSchema
        if objet.get("dateNotification") and int(objet["dateNotification"][:4]) >= 2024:
            data = MarcheSchema.model_validate(objet)
        else:
            data = MarcheAncienSchema.model_validate(objet)

        marche = Marche(
            id=data.id,
            acheteur=self.set_acheteur(
                self.get_or_create_structure(id=data.acheteur.id, type_id="SIRET")
            ),
            nature=data.nature.db_value,
            objet=data.objet,
            code_cpv=data.codeCPV,
            categorie=categorisation.CPV2categorie(data.codeCPV).db_value,
            modalites_execution=[
                mod.db_value
                for mod in data.modalitesExecution["modaliteExecution"]
                if mod.db_value
            ],
            accord_cadre=self.get_accord_cadre(data.idAccordCadre)
            if data.idAccordCadre
            else None,
            marche_innovant=data.marcheInnovant if data.marcheInnovant else False,
            ccag=data.ccag.db_value if data.ccag else None,
            offres_recues=data.offresRecues,
            attribution_avance=(
                data.attributionAvance if data.attributionAvance else False
            ),
            taux_avance=data.tauxAvance,
            type_groupement_operateurs=(
                data.typeGroupementOperateurs.db_value
                if data.typeGroupementOperateurs
                else None
            ),
            sous_traitance_declaree=(
                data.sousTraitanceDeclaree if data.sousTraitanceDeclaree else False
            ),
            procedure=data.procedure.db_value if data.procedure else None,
            lieu=(
                self.get_or_create_lieu(
                    data.lieuExecution.code, data.lieuExecution.typeCode
                )
                if data.lieuExecution
                else None
            ),
            duree_mois=data.dureeMois,
            duree_mois_initiale=data.dureeMois,
            date_notification=data.dateNotification,
            date_publication=(data.datePublicationDonnees),
            montant=data.montant,
            montant_initial=data.montant,
            type_prix=[
                o.db_value
                for o in (data.typesPrix["typePrix"] if data.typesPrix else [])
            ],
            forme_prix=data.formePrix.db_value if data.formePrix else None,
            titulaires=[
                self.set_vendeur(
                    self.get_or_create_structure(
                        id=t["titulaire"].id,
                        type_id=t["titulaire"].typeIdentifiant,
                    )
                )
                for t in data.titulaires
            ],
            origine_ue=data.origineUE,
            origine_france=data.origineFrance,
        )

        for tech in data.techniques["technique"]:
            if tech == TechniqueAchat.AC:
                self._cache_accords_cadre[marche.id] = marche

            if tech.db_value:
                marche.techniques_achat.append(
                    TechniqueAchatMarche(technique=tech.db_value)
                )

        for consideration_sociale in data.considerationsSociales[
            "considerationSociale"
        ]:
            if consideration_sociale.db_value:
                marche.considerations_sociales.append(
                    ConsiderationSocialeMarche(
                        consideration=consideration_sociale.db_value
                    )
                )

        for consideration_env in data.considerationsEnvironnementales[
            "considerationEnvironnementale"
        ]:
            if consideration_env.db_value:
                marche.considerations_environnementales.append(
                    ConsiderationEnvMarche(consideration=consideration_env.db_value)
                )

        index_actes_sous_traitance: dict[int, ActeSousTraitance] = {}
        for tmp in data.actesSousTraitance:
            dacte: ActeSousTraitanceSchema = tmp["acteSousTraitance"]
            acte = ActeSousTraitance(
                id=dacte.id,
                sous_traitant=self.set_vendeur(
                    self.get_or_create_structure(
                        id=dacte.sousTraitant.id,
                        type_id=dacte.sousTraitant.typeIdentifiant,
                    )
                ),
                duree_mois=dacte.dureeMois,
                duree_mois_initiale=dacte.dureeMois,
                date_notification=dacte.dateNotification,
                date_publication=dacte.datePublicationDonnees,
                montant=dacte.montant,
                montant_initial=dacte.montant,
                variation_prix=dacte.variationPrix.db_value,
            )
            marche.actes_sous_traitance.append(acte)
            index_actes_sous_traitance[acte.id] = acte

        for tmp_dma in sorted(
            data.modificationsActesSousTraitance,
            key=lambda x: (
                x[
                    "modificationActeSousTraitance"
                ].dateNotificationModificationSousTraitance
            ),
        ):
            dmodif: ModificationActeSousTraitanceSchema = tmp_dma[
                "modificationActeSousTraitance"
            ]
            if dmodif.id not in index_actes_sous_traitance:
                raise CustomValidationError(
                    errors=[
                        {
                            "type": "incoherence",
                            "loc": ["modificationsActesSousTraitance"],
                            "msg": "L'acte de sous-traitance n'existe pas",
                        }
                    ],
                )
            modif_sous_traitance = ModificationSousTraitance(
                duree_mois=dmodif.dureeMois,
                date_notif=dmodif.dateNotificationModificationSousTraitance,
                date_publication=dmodif.datePublicationDonnees,
                montant=dmodif.montant,
            )
            index_actes_sous_traitance[dmodif.id].modifications.append(
                modif_sous_traitance
            )
            if modif_sous_traitance.duree_mois is not None:
                index_actes_sous_traitance[
                    dmodif.id
                ].duree_mois = modif_sous_traitance.duree_mois
            if modif_sous_traitance.montant is not None:
                index_actes_sous_traitance[
                    dmodif.id
                ].montant = modif_sous_traitance.montant

        for tmp_dm in sorted(data.modifications, key=lambda x: x["modification"].id):
            modif: ModificationMarcheSchema = tmp_dm["modification"]
            titulaires: list[Structure] = []
            if modif.titulaires:
                titulaires = [
                    self.set_vendeur(
                        self.get_or_create_structure(
                            id=titulaire["titulaire"].id,
                            type_id=titulaire["titulaire"].typeIdentifiant,
                        )
                    )
                    for titulaire in modif.titulaires
                ]

            modif_marche = ModificationMarche(
                id=modif.id,
                duree_mois=modif.dureeMois,
                date_notification=modif.dateNotificationModification,
                date_publication=modif.datePublicationDonneesModification,
                montant=modif.montant,
                titulaires=titulaires,
            )
            marche.modifications.append(modif_marche)

            if modif_marche.montant is not None:
                marche.montant = modif_marche.montant
            if modif_marche.duree_mois is not None:
                marche.duree_mois = modif_marche.duree_mois
            if modif_marche.titulaires is not None:
                marche.titulaires = modif_marche.titulaires

        self._session.add(marche)

    def concession_transformer(
        self,
        objet: dict[str, Any],
    ) -> None:
        data = ConcessionSchema.model_validate(objet)

        concession = ContratConcession(
            id=data.id,
            autorite_concedante=self.set_acheteur(
                self.get_or_create_structure(
                    id=data.autoriteConcedante.id, type_id="SIRET"
                )
            ),
            nature=data.nature.db_value,
            objet=data.objet,
            procedure=data.procedure.db_value,
            duree_mois=data.dureeMois,
            duree_mois_initiale=data.dureeMois,
            date_signature=data.dateSignature,
            date_publication=data.datePublicationDonnees,
            date_debut_execution=data.dateDebutExecution,
            valeur_globale=data.valeurGlobale,
            valeur_globale_initiale=data.valeurGlobale,
            montant_subvention_publique=data.montantSubventionPublique,
            considerations_sociales=[
                consideration.db_value
                for consideration in data.considerationsSociales["considerationSociale"]
                if consideration.db_value
            ],
            considerations_environnementales=[
                consideration.db_value
                for consideration in data.considerationsEnvironnementales[
                    "considerationEnvironnementale"
                ]
                if consideration.db_value
            ],
        )

        for tmp in data.donneesExecution:
            dde: DonneeExecutionSchema = tmp["donneesAnnuelles"]
            de = DonneeExecution(
                date_publication=dde.datePublicationDonneesExecution,
                depenses_investissement=dde.depensesInvestissement,
            )
            for tmp_dt in dde.tarifs:
                dt: TarifSchema = tmp_dt["tarif"]
                de.tarifs.append(Tarif(intitule=dt.intituleTarif, tarif=dt.tarif))
            concession.donnees_execution.append(de)

        for tmp_dc in data.concessionnaires:
            data_concessionnaire: ConcessionnaireSchema = tmp_dc["concessionnaire"]
            concession.concessionnaires.append(
                self.set_vendeur(
                    self.get_or_create_structure(
                        id=data_concessionnaire.id,
                        type_id=data_concessionnaire.typeIdentifiant,
                    )
                )
            )

        for tmp_dm in sorted(data.modifications, key=lambda x: x["modification"].id):
            data_modification: ModificationConcessionSchema = tmp_dm["modification"]
            modif_concession = ModificationConcession(
                id=data_modification.id,
                date_signature=data_modification.dateSignatureModification,
                date_publication=data_modification.datePublicationDonneesModification,
                duree_mois=data_modification.dureeMois,
                valeur_globale=data_modification.valeurGlobale,
            )
            concession.modifications.append(modif_concession)
            if modif_concession.valeur_globale is not None:
                concession.valeur_globale = modif_concession.valeur_globale
            if modif_concession.duree_mois is not None:
                concession.duree_mois = modif_concession.duree_mois

        self._session.add(concession)

    def build_entite_erreur(
        self,
        e: ValidationError | CustomValidationError,
        o: dict[str, Any],
        type_contrat: TypeContrat,
    ) -> DecpMalForme:
        def decimal_serializer(obj):  # type: ignore
            if isinstance(obj, Decimal):
                return str(obj)
            raise TypeError

        structure: Structure | None = None

        if type_contrat == TypeContrat.MARCHE and o.get("acheteur", {}).get("id"):
            structure = self.get_or_create_structure(
                id=o["acheteur"]["id"], type_id="SIRET"
            )

        if type_contrat == TypeContrat.CONCESSION and o.get(
            "autoriteConcedante", {}
        ).get("id"):
            structure = self.get_or_create_structure(
                id=o["autoriteConcedante"]["id"], type_id="SIRET"
            )

        date_creation: str | None = None

        if type_contrat == TypeContrat.MARCHE:
            date_creation = o.get("dateNotification")

        if type_contrat == TypeContrat.CONCESSION:
            date_creation = o.get("dateSignature")

        decp = DecpMalForme(
            decp=json.dumps(o, default=decimal_serializer),
            structure=structure,
            date_creation=date.fromisoformat(date_creation) if date_creation else None,
        )

        for erreur in e.errors():
            decp.erreurs.append(
                Erreur(
                    type=erreur["type"],
                    localisation=".".join(
                        str(v) for v in erreur["loc"] if type(v) is not int
                    ),
                    message=erreur["msg"],
                )
            )
        return decp

    def _importer(
        self,
        file: str,
        item_path: str,
        type_contrat: TypeContrat,
        transformer: Callable[[dict[str, Any]], Any],
        batch_commit_size: int = 50_000,
    ) -> None:
        # (ré)Initialisation des valeurs de suivi
        self._valid_objects = 0
        self._invalid_objects = 0
        self._started_at = time.time()

        # Import
        batch_size: int = 0
        with rich.progress.open(file, "rb") as f:
            liste = ijson.items(f, f"{item_path}.item")  # flux objet par objet
            for objet in liste:
                try:
                    transformer(objet)
                    self._valid_objects += 1
                except (ValidationError, CustomValidationError) as e:
                    self._session.add(self.build_entite_erreur(e, objet, type_contrat))
                    self._invalid_objects += 1

                batch_size += 1
                if batch_size >= batch_commit_size:
                    log.info(f"💾 Commit de {batch_size} objets")
                    self._session.commit()
                    batch_size = 0

        self._session.commit()
        self._finished_at = time.time()

        if self._valid_objects + self._invalid_objects:
            log.info(f"⌚ Terminé en {round(self._finished_at - self._started_at, 2)}s")
            log.info(f"✅ Objets valides : {self._valid_objects}")
            log.info(
                f"❌ Objets invalides : {self._invalid_objects} ({round(self._invalid_objects * 100 / (self._valid_objects + self._invalid_objects))}%)"
            )

    def importer_marches(
        self,
        file: str,
        batch_commit_size: int = 100_000,
    ) -> None:
        self._importer(
            file=file,
            item_path="marches.marche",
            transformer=self.marche_transformer,
            batch_commit_size=batch_commit_size,
            type_contrat=TypeContrat.MARCHE,
        )

    def importer_concessions(
        self,
        file: str,
        batch_commit_size: int = 100_000,
    ) -> None:
        self._importer(
            file=file,
            item_path="marches.contrat-concession",
            transformer=self.concession_transformer,
            batch_commit_size=batch_commit_size,
            type_contrat=TypeContrat.CONCESSION,
        )


@app.command()
def decps(import_de_0: bool = False) -> None:  # pragma: no cover
    if import_de_0:
        log.info("🧹 Suppression totale de la base de données")
        engine = get_engine()
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

        with Session(get_engine()) as session:
            session.add_all(import_cpv("cpv_2008_fr.csv"))
            session.commit()
    else:
        log.info(
            "🧹 Suppression partielle de la base de données (lieux et structures conservés)"
        )
        with get_engine().connect() as connexion:
            tables: list[str] = [
                marche_titulaire_table.name,
                modification_titulaire_table.name,
                concession_structure_table.name,
                str(ConsiderationEnvMarche.__tablename__),
                str(ConsiderationSocialeMarche.__tablename__),
                str(TechniqueAchatMarche.__tablename__),
                str(ModificationSousTraitance.__tablename__),
                str(ActeSousTraitance.__tablename__),
                str(ModificationMarche.__tablename__),
                str(Tarif.__tablename__),
                str(DonneeExecution.__tablename__),
                str(Marche.__tablename__),
                str(ModificationConcession.__tablename__),
                str(ContratConcession.__tablename__),
                str(Erreur.__tablename__),
                str(DecpMalForme.__tablename__),
            ]
            connexion.execute(
                text(f"TRUNCATE TABLE {', '.join(tables)} RESTART IDENTITY")
            )
            connexion.commit()

    sources: list[str] = get_config().SOURCES.split(" ")
    RAW_FILE = "./raw_data.json"
    CLEANED_FILE = "./data.json"
    log.info(f"📂 {len(sources)} sources détectées")

    with Session(get_engine()) as session:
        importateur = ImportateurDecp(session=session)

        for source in track(sources):
            log.info(f"🌐 Téléchargement de {source}")
            response = requests.get(source, stream=True)
            response.raise_for_status()
            with open(RAW_FILE, "wb") as handle:
                for block in response.iter_content(1024):
                    handle.write(block)

            log.info("✨ Nettoyage du JSON")
            with open(CLEANED_FILE, "w") as cf:
                with open(f"{RAW_FILE}", "r", errors="ignore") as myFile:
                    for line in myFile:
                        line = line.replace("NaN", "null")
                        cf.write(line)
            os.remove(RAW_FILE)

            log.info("🔄 Import des marchés")
            importateur.importer_marches(file=CLEANED_FILE)

            log.info("🔄 Import des concessions")
            importateur.importer_concessions(file=CLEANED_FILE)

            log.info("🧹 Suppression du fichier téléchargé")
            os.remove(CLEANED_FILE)


@app.command()
def structures() -> None:
    api = get_api_entreprise(get_config())
    with Session(get_engine()) as session:
        structures = list(
            session.execute(
                select(Structure)
                .where(Structure.nom.is_(None), Structure.type_identifiant == "SIRET")
                .order_by(desc(Structure.uid))
            ).scalars()
        )
        log.info(f"{len(structures)} structures sans nom détectées")

        nb: int = 0
        for structure in track(structures):
            try:
                raw = api.raw_donnees_etablissement(
                    f"enrichi/{structure.identifiant}?coordinates_format=WSG84"
                )
                if raw and raw.get("data") and raw["data"].get("unite_legale"):
                    details = raw["data"]
                    structure.nom = (
                        details["unite_legale"]
                        .get("personne_morale_attributs", {})
                        .get("raison_sociale")
                    )
                    structure.cat_entreprise = details["unite_legale"].get(
                        "categorie_entreprise"
                    )
                    if details["coordonnees"]:
                        structure.longitude = details["coordonnees"][0]
                        structure.latitude = details["coordonnees"][1]
                    session.add(structure)
                    log.debug(structure.nom)
                    nb += 1
                    if nb > 500:
                        log.info("💾 Commit de 500 objets")
                        nb = 0
                        session.commit()
            except ApiEntrepriseClientError:
                log.error(
                    f"Erreur ApiEntreprise lors de l'import des données de {structure.identifiant}"
                )

        session.commit()


def load_infogreffe(
    file_path: str, structures: dict[str, int], batch_size: int = 500
) -> Generator[list[StructureInfogreffe], Any, None]:
    with rich.progress.open(file_path, "r") as csvfile:
        total = 0
        existant = 0
        structures_infos = []

        reader = csv.reader(csvfile, delimiter=";")

        headers = next(reader)
        if (
            headers[19] != "millesime_1"
            or headers[25] != "millesime_2"
            or headers[31] != "millesime_3"
        ):
            log.error(
                "Le fichier CSV n'a pas la structure attendue. Importation annulée"
            )
            return

        for row in reader:
            total += 1
            siret = row[1] + row[2]

            if siret in structures:
                existant += 1

                if row[22] or row[23] or row[24]:
                    structures_infos.append(
                        StructureInfogreffe(
                            uid_structure=structures[siret],
                            annee=int(row[19]),
                            ca=Decimal(row[22]) if row[22] else None,
                            resultat=Decimal(row[23]) if row[23] else None,
                            effectif=int(row[24]) if row[24] else None,
                        )
                    )

                if row[28] or row[29] or row[30]:
                    structures_infos.append(
                        StructureInfogreffe(
                            uid_structure=structures[siret],
                            annee=int(row[25]),
                            ca=Decimal(row[28]) if row[28] else None,
                            resultat=Decimal(row[29]) if row[29] else None,
                            effectif=int(row[30]) if row[30] else None,
                        )
                    )

                if row[34] or row[35] or row[36]:
                    structures_infos.append(
                        StructureInfogreffe(
                            uid_structure=structures[siret],
                            annee=int(row[31]),
                            ca=Decimal(row[34]) if row[34] else None,
                            resultat=Decimal(row[35]) if row[35] else None,
                            effectif=int(row[36]) if row[36] else None,
                        )
                    )

                if not existant % batch_size:
                    log.info(f"💾 Commit de {batch_size} structure")
                    yield structures_infos
                    structures_infos = []

    log.info(f"💾 Commit de {len(structures_infos)} structures")
    log.info(f"🧮 Résultat : {existant} entrées utiles {total} au total")
    yield structures_infos


@app.command()
def infogreffe(file_path: str) -> None:
    with get_engine().connect() as connexion:
        connexion.execute(
            text(
                f"TRUNCATE TABLE {str(StructureInfogreffe.__tablename__)} RESTART IDENTITY"
            )
        )
        connexion.commit()
    with Session(get_engine()) as session:
        structures = {
            structure[0]: structure[1]
            for structure in session.execute(
                select(Structure.identifiant, Structure.uid)
            ).all()
        }
        if len(structures):
            log.info(f"{len(structures)} structures détectées")
            for batch in load_infogreffe(file_path, structures):
                session.add_all(batch)
                session.commit()
        else:
            log.error("Aucune structure détectée. Il faut d'abord importer des DECPs.")


def import_cpv(file_path: str) -> list[CPV]:
    log.info("Import des codes CPV dans la base de données")
    entities: list[CPV] = []
    with rich.progress.open(file_path, "r", encoding="latin-1") as csvfile:
        iterator = csv.reader(csvfile, delimiter=";")
        next(iterator)  # ignore header
        for row in iterator:
            entities.append(CPV(code=row[0][:8], libelle=row[1]))
    log.info(f"{len(entities)} codes importés")
    return entities


if __name__ == "__main__":
    app()
