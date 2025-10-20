import os
import sys

sys.path.append(os.getcwd())

import json
import logging
import time
from collections.abc import Callable
from datetime import date, datetime
from decimal import Decimal
from functools import cache
from typing import Any

import ijson
import rich
import rich.progress
import typer
from pydantic_core import ValidationError
from rich.logging import RichHandler
from rich.progress import track
from sqlalchemy import desc, select, text
from sqlalchemy.orm import Session

from app.config import get_config
from app.db import get_engine
from app.dependencies import get_api_entreprise
from app.models.db import (
    ActeSousTraitance,
    Base,
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
    Tarif,
    concession_structure_table,
    marche_titulaire_table,
    modification_titulaire_table,
)
from app.models.dto_importation import (
    ActeSousTraitanceSchema,
    ConcessionnaireSchema,
    ConcessionSchema,
    DonneeExecutionSchema,
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

    def cast_jour(self, data: str) -> date:
        return datetime.fromisoformat(data)

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
        data: MarcheSchema,
    ) -> None:
        marche = Marche(
            id=data.id,
            acheteur=self.set_acheteur(
                self.get_or_create_structure(
                    id=data.acheteur.id,
                )
            ),
            nature=data.nature.db_value,
            objet=data.objet,
            cpv=data.codeCPV,
            techniques_achat=[
                tech.db_value for tech in data.techniques["technique"] if tech.db_value
            ],
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
            date_notification=self.cast_jour(data.dateNotification),
            date_publication=(
                self.cast_jour(data.datePublicationDonnees)
                if data.datePublicationDonnees
                else None
            ),
            montant=data.montant,
            type_prix=[
                o.db_value
                for o in (data.typesPrix["typePrix"] if data.typesPrix else [])
            ],
            forme_prix=data.formePrix.db_value if data.formePrix else None,
            titulaires=[
                self.set_vendeur(
                    self.get_or_create_structure(
                        t["titulaire"].id,
                        t["titulaire"].typeIdentifiant,
                    )
                )
                for t in data.titulaires
            ],
            origine_ue=data.origineUE,
            origine_france=data.origineFrance,
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

        if TechniqueAchat.AC.db_value in marche.techniques_achat:
            self._cache_accords_cadre[marche.id] = marche

        index_actes_sous_traitance: dict[int, ActeSousTraitance] = {}
        for tmp in data.actesSousTraitance:
            dacte: ActeSousTraitanceSchema = tmp["acteSousTraitance"]
            acte = ActeSousTraitance(
                id=dacte.id,
                sous_traitant=self.set_vendeur(
                    self.get_or_create_structure(
                        type_id=dacte.sousTraitant.typeIdentifiant,
                        id=dacte.sousTraitant.id,
                    )
                ),
                duree_mois=dacte.dureeMois,
                date_notification=self.cast_jour(dacte.dateNotification),
                date_publication=self.cast_jour(dacte.datePublicationDonnees),
                montant=dacte.montant,
                variation_prix=dacte.variationPrix.db_value,
            )
            marche.actes_sous_traitance.append(acte)
            index_actes_sous_traitance[acte.id] = acte

        for tmp_dma in data.modificationsActesSousTraitance:
            dmodif: ModificationActeSousTraitanceSchema = (
                tmp_dma["modificationActeSousTraitance"]
                if "modificationActeSousTraitance" in tmp_dma
                else tmp_dma["modificationActesSousTraitance"]
            )
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
            index_actes_sous_traitance[dmodif.id].modifications.append(
                ModificationSousTraitance(
                    duree_mois=dmodif.dureeMois,
                    date_notif=self.cast_jour(
                        dmodif.dateNotificationModificationActeSousTraitance
                    ),
                    date_publication=self.cast_jour(
                        dmodif.datePublicationDonneesModificationActeSousTraitance
                    ),
                    montant=dmodif.montant,
                )
            )

        for tmp_dm in data.modifications:
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

            marche.modifications.append(
                ModificationMarche(
                    id=modif.id,
                    duree_mois=modif.dureeMois,
                    date_notification=self.cast_jour(
                        modif.dateNotificationModification
                    ),
                    date_publication=self.cast_jour(
                        modif.datePublicationDonneesModification
                    ),
                    montant=modif.montant,
                    titulaires=titulaires,
                )
            )

        self._session.add(marche)

    def concession_transformer(
        self,
        data: ConcessionSchema,
    ) -> None:
        concession = ContratConcession(
            id=data.id,
            autorite_concedante=self.set_acheteur(
                self.get_or_create_structure(
                    id=data.autoriteConcedante.id,
                )
            ),
            nature=data.nature.db_value,
            objet=data.objet,
            procedure=data.procedure.db_value,
            duree_mois=data.dureeMois,
            date_signature=self.cast_jour(data.dateSignature),
            date_publication=self.cast_jour(data.datePublicationDonnees),
            date_debut_execution=self.cast_jour(data.dateDebutExecution),
            valeur_globale=data.valeurGlobale,
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
                date_publication=self.cast_jour(dde.datePublicationDonneesExecution),
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

        for tmp_dm in data.modifications:
            data_modification: ModificationConcessionSchema = tmp_dm["modification"]
            concession.modifications.append(
                ModificationConcession(
                    id=data_modification.id,
                    date_signature=self.cast_jour(
                        data_modification.dateSignatureModification
                    ),
                    date_publication=self.cast_jour(
                        data_modification.datePublicationDonneesModification
                    ),
                    duree_mois=data_modification.dureeMois,
                    valeur_globale=data_modification.valeurGlobale,
                )
            )
        self._session.add(concession)

    def build_entite_erreur(
        self, e: ValidationError | CustomValidationError, o: dict[str, Any]
    ) -> DecpMalForme:
        def decimal_serializer(obj):  # type: ignore
            if isinstance(obj, Decimal):
                return str(obj)
            raise TypeError

        decp = DecpMalForme(decp=json.dumps(o, default=decimal_serializer))
        for erreur in e.errors():
            decp.erreurs.append(
                Erreur(
                    type=erreur["type"],
                    localisation=".".join(str(v) for v in erreur["loc"]),
                    message=erreur["msg"],
                )
            )
        return decp

    def _importer(
        self,
        file: str,
        item_path: str,
        schema: type[MarcheSchema] | type[ConcessionSchema],
        transformer: Callable[[ConcessionSchema], Any] | Callable[[MarcheSchema], Any],
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
                    transformer(
                        schema.model_validate(objet)  # type: ignore
                    )
                    self._valid_objects += 1
                except (ValidationError, CustomValidationError) as e:
                    self._session.add(self.build_entite_erreur(e, objet))
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
            schema=MarcheSchema,
            transformer=self.marche_transformer,
            batch_commit_size=batch_commit_size,
        )

    def importer_concessions(
        self,
        file: str,
        batch_commit_size: int = 100_000,
    ) -> None:
        self._importer(
            file=file,
            item_path="marches.contrat-concession",
            schema=ConcessionSchema,
            transformer=self.concession_transformer,
            batch_commit_size=batch_commit_size,
        )


@app.command()
def decps(import_de_0: bool = False) -> None:  # pragma: no cover
    if import_de_0:
        log.info("🧹 Suppression totale de la base de données")
        Base.metadata.drop_all(get_engine())
        get_engine()
    else:
        log.info(
            "🧹 Suppression partielle de la base de données (lieux et structures conservés)"
        )
        with get_engine().connect() as connexion:
            tables: list[str] = [
                marche_titulaire_table.name,
                modification_titulaire_table.name,
                concession_structure_table.name,
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

    WORKING_PATH: str = "./data/"

    with Session(get_engine()) as session:
        importateur = ImportateurDecp(session=session)

        for raw_file in track(os.listdir(WORKING_PATH)):
            if raw_file == "tmp":
                continue

            log.info(f"📂 Détection de {WORKING_PATH}{raw_file}")

            log.info("✨ Nettoyage du JSON")
            tmp: str = f"{WORKING_PATH}tmp"
            f = open(tmp, "w")
            with open(f"{WORKING_PATH}{raw_file}", "r", errors="ignore") as myFile:
                for line in myFile:
                    line = line.replace("NaN", "null")
                    f.write(line)
            f.close()

            log.info("🔄 Import des marchés")
            importateur.importer_marches(file=tmp)

            log.info("🔄 Import des concessions")
            importateur.importer_concessions(file=tmp)


@app.command()
def noms_structures() -> None:
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
            data = api.donnees_etablissement(structure.identifiant)
            if (
                data
                and data.unite_legale
                and data.unite_legale.personne_morale_attributs
            ):
                structure.nom = (
                    data.unite_legale.personne_morale_attributs.raison_sociale
                )
                session.add(structure)
                log.debug(structure.nom)
                nb += 1
                if nb > 500:
                    log.info("💾 Commit de 500 objets")
                    nb = 0
                    session.commit()

        session.commit()


if __name__ == "__main__":
    app()
