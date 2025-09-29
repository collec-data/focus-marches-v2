from datetime import date
import re
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, Text, ForeignKey, Table, Column
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    declared_attr,
)
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.types import PickleType

from .enums import *


class Base(DeclarativeBase):
    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:  # type: ignore
        # On transforme le nom de CamelCase à snake_case
        return re.sub(r"(?!^)([A-Z]+)", r"_\1", cls.__name__).lower()


marche_titulaire_table = Table(
    "marche_titulaire_table",
    Base.metadata,
    Column("uid_marche", ForeignKey("marche.uid")),
    Column("uid_titulaire", ForeignKey("structure.uid")),
)


class Structure(Base):
    uid: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    identifiant: Mapped[str]
    type_identifiant: Mapped[str]
    vendeur: Mapped[bool] = mapped_column(default=False)
    acheteur: Mapped[bool] = mapped_column(default=False)
    marches_acheteurs: Mapped[list["Marche"]] = relationship(back_populates="acheteur")
    marches_vendeur: Mapped[list["Marche"]] = relationship(
        back_populates="titulaires", secondary=marche_titulaire_table
    )


class ModificationSousTraitance(Base):
    uid: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uid_acte_sous_traitance: Mapped[int] = mapped_column(
        ForeignKey("acte_sous_traitance.uid")
    )
    duree_mois: Mapped[int | None]
    date_notif: Mapped[date]
    date_publication: Mapped[date]
    montant: Mapped[Decimal | None]


class ActeSousTraitance(Base):
    uid: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uid_marche: Mapped[int] = mapped_column(ForeignKey("marche.uid"))
    id: Mapped[int]  # unique par marché, dans l'ordre de création
    sous_traitant: Mapped[Structure] = relationship()  # 1*
    uid_sous_traitant: Mapped[int] = mapped_column(ForeignKey("structure.uid"))
    duree_mois: Mapped[int | None]
    date_notification: Mapped[date]
    date_publication: Mapped[date]
    montant: Mapped[Decimal]
    variation_prix: Mapped[int | None]  # enum VariationPrix
    modifications: Mapped[list[ModificationSousTraitance]] = relationship()


modification_titulaire_table = Table(
    "modification_titulaire_table",
    Base.metadata,
    Column("uid_modification", ForeignKey("modification_marche.uid")),
    Column("uid_titulaire", ForeignKey("structure.uid")),
)


class ModificationMarche(Base):
    uid: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uid_marche: Mapped[int] = mapped_column(ForeignKey("marche.uid"))
    id: Mapped[int]  # id unique croissant par marché
    duree_mois: Mapped[int | None]
    date_notification: Mapped[date]
    date_publication: Mapped[date]
    montant: Mapped[Decimal | None]
    titulaires: Mapped[list[Structure]] = relationship(
        secondary=modification_titulaire_table
    )  # **


class Lieu(Base):
    uid: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str]
    type_code: Mapped[int]


class Tarif(Base):
    uid: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uid_donnee_execution: Mapped[int] = mapped_column(
        ForeignKey("donnee_execution.uid")
    )
    intitule: Mapped[str]
    tarif: Mapped[Decimal]


class DonneeExecution(Base):
    uid: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uid_contrat_concession: Mapped[int] = mapped_column(
        ForeignKey("contrat_concession.uid")
    )
    date_publication: Mapped[date]
    depenses_investissement: Mapped[Decimal]  # nbr
    tarifs: Mapped[list[Tarif]] = relationship()


class Marche(Base):
    uid: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id: Mapped[str]
    acheteur: Mapped[Structure] = relationship()  # 1*
    uid_acheteur: Mapped[int] = mapped_column(ForeignKey("structure.uid"))
    nature: Mapped[int | None]  # enum NatureMarche
    objet: Mapped[str] = mapped_column(Text())  # max 1k
    cpv: Mapped[str]
    techniques_achat: Mapped[list[TechniqueAchat]] = mapped_column(
        MutableList.as_mutable(PickleType)
    )
    modalites_execution: Mapped[list[ModaliteExecution]] = mapped_column(
        MutableList.as_mutable(PickleType)
    )
    accord_cadre: Mapped[Optional["Marche"]] = relationship()  # 1*
    uid_accord_cadre: Mapped[None | int] = mapped_column(ForeignKey("marche.uid"))
    marche_innovant: Mapped[bool]
    ccag: Mapped[int | None]
    offres_recues: Mapped[int | None]
    attribution_avance: Mapped[bool]
    taux_avance: Mapped[Decimal]
    type_groupement_operateurs: Mapped[int | None]  # enum TypeGroupementOperateur
    sous_traitance_declaree: Mapped[bool]
    actes_sous_traitance: Mapped[list[ActeSousTraitance]] = relationship()
    procedure: Mapped[int | None]  # enum ProcedureMarche
    lieu: Mapped[Lieu] = relationship()  # 1*
    uid_lieu: Mapped[int | None] = mapped_column(ForeignKey("lieu.uid"))
    duree_mois: Mapped[int]
    date_notification: Mapped[date]
    date_publication: Mapped[date | None]
    montant: Mapped[Decimal]
    type_prix: Mapped[list[TypePrix]] = mapped_column(
        MutableList.as_mutable(PickleType)
    )  # enum TypePrix
    forme_prix: Mapped[int | None]  # enum FormePrix
    origine_ue: Mapped[Decimal | None]
    origine_france: Mapped[Decimal | None]
    titulaires: Mapped[list[Structure]] = relationship(
        secondary=marche_titulaire_table
    )  # **
    considerations_sociales: Mapped[list[ConsiderationsSociales]] = mapped_column(
        MutableList.as_mutable(PickleType)
    )
    considerations_environnementales: Mapped[list[ConsiderationsEnvironnementales]] = (
        mapped_column(MutableList.as_mutable(PickleType))
    )
    # modifications_actes_sous_traitance: Mapped[list[ModificationSousTraitance]] = (
    #     relationship()
    # )  # *1
    modifications: Mapped[list[ModificationMarche]] = relationship()  # *1


class ModificationConcession(Base):
    uid: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uid_concession: Mapped[int] = mapped_column(ForeignKey("contrat_concession.uid"))
    id: Mapped[int]  # id unique croissant par concession
    date_signature: Mapped[date]
    date_publication: Mapped[date]
    duree_mois: Mapped[int | None] = mapped_column(default=None)
    valeur_globale: Mapped[Decimal | None] = mapped_column(default=None)


concession_structure_table = Table(
    "concession_structure_table",
    Base.metadata,
    Column("uid_concession", ForeignKey("contrat_concession.uid")),
    Column("uid_concessionnaire", ForeignKey("structure.uid")),
)


class ContratConcession(Base):
    uid: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id: Mapped[str]  # interne propre à l'acheteur donc pas utilisable en pk
    autorite_concedante: Mapped[Structure] = relationship()  # 1*
    uid_autorite: Mapped[int] = mapped_column(ForeignKey("structure.uid"))
    nature: Mapped[int | None]  # enum NatureConcession
    objet: Mapped[str] = mapped_column(String(1_000))
    procedure: Mapped[int]  # enum ProcédureConcession
    duree_mois: Mapped[int]
    date_signature: Mapped[date]
    date_publication: Mapped[date]
    date_debut_execution: Mapped[date]
    valeur_globale: Mapped[Decimal]
    montant_subvention_publique: Mapped[Decimal]
    donnees_execution: Mapped[list[DonneeExecution]] = relationship()  # *1
    concessionnaires: Mapped[list[Structure]] = relationship(
        secondary=concession_structure_table
    )  # **
    considerations_sociales: Mapped[list[ConsiderationsSociales]] = mapped_column(
        MutableList.as_mutable(PickleType)
    )
    considerations_environnementales: Mapped[list[ConsiderationsEnvironnementales]] = (
        mapped_column(MutableList.as_mutable(PickleType))
    )
    modifications: Mapped[list[ModificationConcession]] = relationship()  # *1


class Erreur(Base):
    uid: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uid_decp: Mapped[int] = mapped_column(ForeignKey("decp_mal_forme.uid"))
    type: Mapped[str]
    localisation: Mapped[str]
    message: Mapped[str]


class DecpMalForme(Base):
    uid: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    decp: Mapped[str]
    erreurs: Mapped[list[Erreur]] = relationship()
