import os
import sys

sys.path.append(os.getcwd())

import json
import time
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Callable

import ijson
from api_entreprise.api import ApiEntreprise
from pydantic_core import ValidationError
from sqlalchemy import select
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
from app.models.enums import TypeCodeLieu


class CustomValidationError(Exception):
    def __init__(
        self, message: str = "", errors: list[dict[str, str | list[str]]] = []
    ):
        super().__init__(message)
        self._errors = errors

    def errors(self) -> list[dict[str, str | list[str]]]:
        return self._errors


class ImportateurDecp:
    def __init__(
        self,
        session: Session,
        file: str,
        objet_type: str,
        api_entreprise: ApiEntreprise | None = None,
    ):
        self._cache_lieux: dict[str, Lieu] = {}
        self._cache_structures: dict[str, Structure] = {}

        self._valid_objects: int = 0
        self._invalid_objects: int = 0

        self._started_at: float = time.time()
        self._finished_at: float

        self._session: Session = session
        self._api_entreprise: ApiEntreprise | None = api_entreprise
        self._file: str = file

        self._item_path: str
        self._schema: type[MarcheSchema] | type[ConcessionSchema]
        self._transformer: (
            Callable[[ConcessionSchema], Any] | Callable[[MarcheSchema], Any]
        )
        if objet_type == "marche":
            self._item_path = "marches.marche"
            self._schema = MarcheSchema
            self._transformer = self.marche_transformer
        elif objet_type == "concession":
            self._item_path = "marches.contrat-concession"
            self._schema = ConcessionSchema
            self._transformer = self.concession_transformer
        else:
            raise ValueError

    def cast_jour(self, data: str) -> date:
        date_format_jour = "%Y-%m-%d"  # eg 2020-05-15
        return datetime.strptime(data, date_format_jour)

    def get_or_create_structure(
        self,
        id: str,
        type_id: str = "SIRET",
        set_is_acheteur: bool = False,
        set_is_vendeur: bool = False,
    ) -> Structure:
        if id + type_id in self._cache_structures.keys():
            return self._cache_structures[id + type_id]

        structure: Structure | None = self._session.execute(
            select(Structure)
            .where(Structure.identifiant == id)
            .where(Structure.type_identifiant == type_id)
        ).scalar()

        if not structure:
            structure = Structure(identifiant=id, type_identifiant=type_id)

            if type_id == "SIRET" and self._api_entreprise:
                data = self._api_entreprise.donnees_etablissement(id)

                if (
                    data
                    and data.unite_legale
                    and data.unite_legale.personne_morale_attributs
                ):
                    structure.nom = (
                        data.unite_legale.personne_morale_attributs.raison_sociale
                    )

        if set_is_acheteur:
            structure.acheteur = True
        if set_is_vendeur:
            structure.vendeur = True

        self._cache_structures[id + type_id] = structure

        return structure

    def get_or_create_lieu(self, code: str, type_code: TypeCodeLieu) -> Lieu:
        if code + str(type_code.db_value) in self._cache_lieux:
            return self._cache_lieux[code + str(type_code.db_value)]

        lieu = self._session.execute(
            select(Lieu)
            .where(Lieu.code == code)
            .where(Lieu.type_code == type_code.db_value)
        ).scalar()
        if not lieu:
            lieu = Lieu(
                code=code,
                type_code=type_code.db_value,
            )
        self._cache_lieux[code + str(type_code.db_value)] = lieu
        return lieu

    def marche_transformer(
        self,
        data: MarcheSchema,
    ) -> None:
        accord_cadre: Marche | None = None
        # if data.idAccordCadre:
        #     accord_cadre = self._session.execute(
        #         select(Marche).where(Marche.id == data.idAccordCadre)
        #     ).one_or_none()

        marche = Marche(
            id=data.id,
            acheteur=self.get_or_create_structure(
                id=data.acheteur.id,
                set_is_acheteur=True,
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
            accord_cadre=accord_cadre,
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
                self.get_or_create_structure(
                    t["titulaire"].id,
                    t["titulaire"].typeIdentifiant,
                    set_is_vendeur=True,
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

        index_actes_sous_traitance: dict[int, ActeSousTraitance] = {}
        for tmp in data.actesSousTraitance:
            dacte: ActeSousTraitanceSchema = tmp["acteSousTraitance"]
            acte = ActeSousTraitance(
                id=dacte.id,
                sous_traitant=self.get_or_create_structure(
                    type_id=dacte.sousTraitant.typeIdentifiant,
                    id=dacte.sousTraitant.id,
                    set_is_vendeur=True,
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
                    self.get_or_create_structure(
                        id=titulaire["titulaire"].id,
                        type_id=titulaire["titulaire"].typeIdentifiant,
                        set_is_vendeur=True,
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
            autorite_concedante=self.get_or_create_structure(
                id=data.autoriteConcedante.id,
                set_is_acheteur=True,
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
                self.get_or_create_structure(
                    id=data_concessionnaire.id,
                    type_id=data_concessionnaire.typeIdentifiant,
                    set_is_vendeur=True,
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
        self._session.commit()

    def build_entite_erreur(
        self, e: ValidationError | CustomValidationError, o: dict[str, Any]
    ) -> DecpMalForme:
        def decimal_serializer(obj):  # type: ignore
            if isinstance(obj, Decimal):
                return str(obj)
            raise TypeError

        decp = DecpMalForme(decp=json.dumps(o, default=decimal_serializer))
        for erreur in e.errors():
            # print(
            #     f"> {erreur["type"]} - {".".join(str(v) for v in erreur["loc"])} - {erreur["msg"]}"
            # )
            decp.erreurs.append(
                Erreur(
                    type=erreur["type"],
                    localisation=".".join(str(v) for v in erreur["loc"]),
                    message=erreur["msg"],
                )
            )
        return decp

    def importer(self) -> "ImportateurDecp":
        with open(self._file, "rb") as f:
            liste = ijson.items(f, f"{self._item_path}.item")  # flux objet par objet
            for objet in liste:
                try:
                    self._transformer(
                        self._schema.model_validate(objet)  # type: ignore
                    )
                    self._valid_objects += 1
                except (ValidationError, CustomValidationError) as e:
                    self._session.add(self.build_entite_erreur(e, objet))
                    self._invalid_objects += 1
        self._session.commit()
        self._finished_at = time.time()
        return self

    def print_stats(self) -> None:
        if self._valid_objects + self._invalid_objects:
            print(
                f"Import de {self._item_path}\n> Terminé en {round(self._finished_at - self._started_at, 2)}s\n> Objets valides : {self._valid_objects}\n> Objets invalides : {self._invalid_objects} ({round(self._invalid_objects * 100 / (self._valid_objects + self._invalid_objects))}%)"
            )


if __name__ == "__main__":  # pragma: no cover
    Base.metadata.drop_all(get_engine())  # ToDo remove after tests
    Base.metadata.create_all(get_engine())

    working_path: str = "./data/"
    for raw_file in os.listdir(working_path):
        tmp: str = f"{working_path}tmp"
        # clean invalid json
        f = open(tmp, "w")
        print(f"{working_path}{raw_file}")
        with open(f"{working_path}{raw_file}", "r", errors="ignore") as myFile:
            for line in myFile:
                line = line.replace("NaN", "null")
                f.write(line)
        f.close()

        with Session(get_engine()) as session:
            ImportateurDecp(
                session=session,
                file=tmp,
                objet_type="marche",
                api_entreprise=get_api_entreprise(get_config()),
            ).importer().print_stats()
            ImportateurDecp(
                session=session,
                file=tmp,
                objet_type="concession",
                api_entreprise=get_api_entreprise(get_config()),
            ).importer().print_stats()
