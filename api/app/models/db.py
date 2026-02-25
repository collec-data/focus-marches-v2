import re
from datetime import date
from decimal import Decimal

from sqlalchemy import Column, ForeignKey, String, Table, Text, UniqueConstraint
from sqlalchemy.dialects.mysql import DECIMAL
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
    relationship,
)
from sqlalchemy.types import PickleType

from app.models.enums import (
    CategorieMarche,
    ConsiderationsEnvironnementales,
    ConsiderationsSociales,
    FormePrix,
    ModaliteExecution,
    NatureConcession,
    NatureMarche,
    ProcedureConcession,
    ProcedureMarche,
    TechniqueAchat,
    TypeCodeLieu,
    TypeGroupementOperateur,
    TypePrix,
    VariationPrix,
)


class Base(DeclarativeBase):
    @declared_attr  # type: ignore
    def __tablename__(cls: "Base") -> str:
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
    identifiant: Mapped[str] = mapped_column(String(50))
    type_identifiant: Mapped[str] = mapped_column(String(10))
    nom: Mapped[str | None] = mapped_column(String(255), default=None)
    vendeur: Mapped[bool] = mapped_column(default=False)
    acheteur: Mapped[bool] = mapped_column(default=False)
    cat_entreprise: Mapped[str | None] = mapped_column(String(10), default=None)
    marches_acheteurs: Mapped[list["Marche"]] = relationship(back_populates="acheteur")
    marches_vendeur: Mapped[list["Marche"]] = relationship(
        back_populates="titulaires", secondary=marche_titulaire_table
    )
    longitude: Mapped[float | None] = mapped_column(default=None)
    latitude: Mapped[float | None] = mapped_column(default=None)
    infogreffe: Mapped[list["StructureInfogreffe"]] = relationship(
        back_populates="structure"
    )

    __table_args__ = (UniqueConstraint("identifiant", "type_identifiant"),)


class StructureInfogreffe(Base):
    uid: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uid_structure: Mapped[int] = mapped_column(ForeignKey("structure.uid"))
    structure: Mapped[Structure] = relationship(back_populates="infogreffe")
    annee: Mapped[int]
    ca: Mapped[Decimal | None] = mapped_column(DECIMAL(12, 2), default=None)
    resultat: Mapped[Decimal | None] = mapped_column(DECIMAL(12, 2), default=None)
    effectif: Mapped[int | None]


class ModificationSousTraitance(Base):
    uid: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uid_acte_sous_traitance: Mapped[int] = mapped_column(
        ForeignKey("acte_sous_traitance.uid")
    )
    duree_mois: Mapped[int | None]
    date_notif: Mapped[date]
    date_publication: Mapped[date]
    montant: Mapped[Decimal | None] = mapped_column(DECIMAL(12, 2), default=None)


class ActeSousTraitance(Base):
    uid: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uid_marche: Mapped[int] = mapped_column(ForeignKey("marche.uid"))
    id: Mapped[int]  # unique par marché, dans l'ordre de création
    sous_traitant: Mapped[Structure] = relationship()  # 1*
    uid_sous_traitant: Mapped[int] = mapped_column(ForeignKey("structure.uid"))
    duree_mois: Mapped[int | None]
    duree_mois_initiale: Mapped[int | None]
    date_notification: Mapped[date]
    date_publication: Mapped[date]
    montant: Mapped[Decimal] = mapped_column(DECIMAL(12, 2))
    montant_initial: Mapped[Decimal] = mapped_column(DECIMAL(12, 2))
    variation_prix: Mapped[int | None]  # enum VariationPrix
    modifications: Mapped[list[ModificationSousTraitance]] = relationship()

    @hybrid_property
    def variation_prix_as_str(self) -> VariationPrix | None:
        return (
            VariationPrix.from_db_value(self.variation_prix)
            if self.variation_prix
            else None
        )


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
    montant: Mapped[Decimal | None] = mapped_column(DECIMAL(12, 2))
    titulaires: Mapped[list[Structure]] = relationship(
        secondary=modification_titulaire_table
    )  # **


class Lieu(Base):
    uid: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(10))
    type_code: Mapped[int]

    @hybrid_property
    def type_code_as_str(self) -> TypeCodeLieu:
        return TypeCodeLieu.from_db_value(self.type_code)

    __table_args__ = (UniqueConstraint("code", "type_code"),)


class Tarif(Base):
    uid: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uid_donnee_execution: Mapped[int] = mapped_column(
        ForeignKey("donnee_execution.uid")
    )
    intitule: Mapped[str] = mapped_column(String(255))
    tarif: Mapped[Decimal] = mapped_column(DECIMAL(12, 2))


class DonneeExecution(Base):
    uid: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uid_contrat_concession: Mapped[int] = mapped_column(
        ForeignKey("contrat_concession.uid")
    )
    date_publication: Mapped[date]
    depenses_investissement: Mapped[Decimal] = mapped_column(DECIMAL(12, 2))
    tarifs: Mapped[list[Tarif]] = relationship()


class ConsiderationEnvMarche(Base):
    uid: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uid_marche: Mapped[int] = mapped_column(ForeignKey("marche.uid"))
    consideration: Mapped[int]


class ConsiderationSocialeMarche(Base):
    uid: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uid_marche: Mapped[int] = mapped_column(ForeignKey("marche.uid"))
    consideration: Mapped[int]


class TechniqueAchatMarche(Base):
    uid: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uid_marche: Mapped[int] = mapped_column(ForeignKey("marche.uid"))
    technique: Mapped[int]


class Marche(Base):
    uid: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id: Mapped[str] = mapped_column(String(16))
    acheteur: Mapped[Structure] = relationship()  # 1*
    uid_acheteur: Mapped[int] = mapped_column(ForeignKey("structure.uid"))
    nature: Mapped[int]  # enum NatureMarche
    objet: Mapped[str] = mapped_column(Text())  # max 1k
    code_cpv: Mapped[int] = mapped_column(ForeignKey("cpv.code"))
    cpv: Mapped[CPV] = relationship()
    categorie: Mapped[int]  # enum CategorieMarche
    techniques_achat: Mapped[list[TechniqueAchatMarche]] = relationship()
    modalites_execution: Mapped[list[int]] = mapped_column(
        MutableList.as_mutable(PickleType)
    )
    accord_cadre: Mapped["Marche | None"] = relationship()  # 1*
    uid_accord_cadre: Mapped[None | int] = mapped_column(ForeignKey("marche.uid"))
    marche_innovant: Mapped[bool]
    ccag: Mapped[int | None]
    offres_recues: Mapped[int | None]
    attribution_avance: Mapped[bool]
    taux_avance: Mapped[Decimal] = mapped_column(DECIMAL(12, 2))
    type_groupement_operateurs: Mapped[int | None]  # enum TypeGroupementOperateur
    sous_traitance_declaree: Mapped[bool]
    actes_sous_traitance: Mapped[list[ActeSousTraitance]] = relationship()
    procedure: Mapped[int | None]  # enum ProcedureMarche
    lieu: Mapped[Lieu] = relationship()  # 1*
    uid_lieu: Mapped[int | None] = mapped_column(ForeignKey("lieu.uid"))
    duree_mois: Mapped[int]
    duree_mois_initiale: Mapped[int]
    date_notification: Mapped[date]
    date_publication: Mapped[date | None]
    montant: Mapped[Decimal] = mapped_column(DECIMAL(12, 2))
    montant_initial: Mapped[Decimal] = mapped_column(DECIMAL(12, 2))
    type_prix: Mapped[list[int]] = mapped_column(
        MutableList.as_mutable(PickleType)
    )  # enum TypePrix
    forme_prix: Mapped[int | None]  # enum FormePrix
    origine_ue: Mapped[Decimal | None] = mapped_column(DECIMAL(12, 2))
    origine_france: Mapped[Decimal | None] = mapped_column(DECIMAL(12, 2))
    titulaires: Mapped[list[Structure]] = relationship(
        secondary=marche_titulaire_table
    )  # **
    considerations_sociales: Mapped[list[ConsiderationSocialeMarche]] = relationship()
    considerations_environnementales: Mapped[list[ConsiderationEnvMarche]] = (
        relationship()
    )
    # modifications_actes_sous_traitance: Mapped[list[ModificationSousTraitance]] = (
    #     relationship()
    # )  # *1
    modifications: Mapped[list[ModificationMarche]] = relationship()  # *1

    @hybrid_property
    def nature_as_str(self) -> NatureMarche:
        return NatureMarche.from_db_value(self.nature)

    @hybrid_property
    def categorie_as_str(self) -> CategorieMarche:
        return CategorieMarche.from_db_value(self.categorie)

    @hybrid_property
    def procedure_as_str(self) -> ProcedureMarche | None:
        return ProcedureMarche.from_db_value(self.procedure) if self.procedure else None

    @hybrid_property
    def forme_prix_as_str(self) -> FormePrix | None:
        return FormePrix.from_db_value(self.forme_prix) if self.forme_prix else None

    @hybrid_property
    def type_prix_as_str(self) -> list[TypePrix]:
        return [TypePrix.from_db_value(v) for v in self.type_prix]

    @hybrid_property
    def considerations_sociales_as_str(self) -> list[ConsiderationsSociales]:
        return [
            ConsiderationsSociales.from_db_value(c.consideration)
            for c in self.considerations_sociales
        ]

    @hybrid_property
    def considerations_environnementales_as_str(
        self,
    ) -> list[ConsiderationsEnvironnementales]:
        return [
            ConsiderationsEnvironnementales.from_db_value(c.consideration)
            for c in self.considerations_environnementales
        ]

    @hybrid_property
    def type_groupement_operateurs_as_str(self) -> TypeGroupementOperateur | None:
        return (
            TypeGroupementOperateur.from_db_value(self.type_groupement_operateurs)
            if self.type_groupement_operateurs
            else None
        )

    @hybrid_property
    def techniques_achat_as_str(self) -> list[TechniqueAchat]:
        return [
            TechniqueAchat.from_db_value(t.technique) for t in self.techniques_achat
        ]

    @hybrid_property
    def modalites_execution_as_str(self) -> list[ModaliteExecution]:
        return [ModaliteExecution.from_db_value(v) for v in self.modalites_execution]


class ModificationConcession(Base):
    uid: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uid_concession: Mapped[int] = mapped_column(ForeignKey("contrat_concession.uid"))
    id: Mapped[int]  # id unique croissant par concession
    date_signature: Mapped[date]
    date_publication: Mapped[date]
    duree_mois: Mapped[int | None] = mapped_column(default=None)
    valeur_globale: Mapped[Decimal | None] = mapped_column(DECIMAL(12, 2), default=None)


concession_structure_table = Table(
    "concession_structure_table",
    Base.metadata,
    Column("uid_concession", ForeignKey("contrat_concession.uid")),
    Column("uid_concessionnaire", ForeignKey("structure.uid")),
)


class ContratConcession(Base):
    uid: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id: Mapped[str] = mapped_column(String(16))
    autorite_concedante: Mapped[Structure] = relationship()  # 1*
    uid_autorite: Mapped[int] = mapped_column(ForeignKey("structure.uid"))
    nature: Mapped[int | None]  # enum NatureConcession
    objet: Mapped[str] = mapped_column(String(1_000))
    procedure: Mapped[int]  # enum ProcédureConcession
    duree_mois: Mapped[int]
    duree_mois_initiale: Mapped[int]
    date_signature: Mapped[date]
    date_publication: Mapped[date]
    date_debut_execution: Mapped[date]
    valeur_globale: Mapped[Decimal] = mapped_column(DECIMAL(12, 2))
    valeur_globale_initiale: Mapped[Decimal] = mapped_column(DECIMAL(12, 2))
    montant_subvention_publique: Mapped[Decimal] = mapped_column(DECIMAL(12, 2))
    donnees_execution: Mapped[list[DonneeExecution]] = relationship()  # *1
    concessionnaires: Mapped[list[Structure]] = relationship(
        secondary=concession_structure_table
    )  # **
    considerations_sociales: Mapped[list[int]] = mapped_column(
        MutableList.as_mutable(PickleType)
    )
    considerations_environnementales: Mapped[list[int]] = mapped_column(
        MutableList.as_mutable(PickleType)
    )
    modifications: Mapped[list[ModificationConcession]] = relationship()  # *1

    @hybrid_property
    def nature_as_str(self) -> NatureConcession | None:
        return NatureConcession.from_db_value(self.nature) if self.nature else None

    @hybrid_property
    def procedure_as_str(self) -> ProcedureConcession | None:
        return (
            ProcedureConcession.from_db_value(self.procedure)
            if self.procedure
            else None
        )

    @hybrid_property
    def considerations_sociales_as_str(self) -> list[ConsiderationsSociales]:
        return [
            ConsiderationsSociales.from_db_value(v)
            for v in self.considerations_sociales
        ]

    @hybrid_property
    def considerations_environnementales_as_str(
        self,
    ) -> list[ConsiderationsEnvironnementales]:
        return [
            ConsiderationsEnvironnementales.from_db_value(v)
            for v in self.considerations_environnementales
        ]


class Erreur(Base):
    uid: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    decp: Mapped["DecpMalForme"] = relationship()
    uid_decp: Mapped[int] = mapped_column(ForeignKey("decp_mal_forme.uid"))
    type: Mapped[str] = mapped_column(String(100))
    localisation: Mapped[str] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(String(255))


class DecpMalForme(Base):
    uid: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    decp: Mapped[str] = mapped_column(Text())
    erreurs: Mapped[list[Erreur]] = relationship(back_populates="decp")
    uid_structure: Mapped[int | None] = mapped_column(
        ForeignKey(Structure.uid), default=None
    )
    structure: Mapped[Structure | None] = relationship()
    date_creation: Mapped[date | None]


class CPV(Base):
    __tablename__ = "cpv"  # type: ignore
    code: Mapped[int] = mapped_column(primary_key=True)
    libelle: Mapped[str] = mapped_column(String(255))


class Conf(Base):
    clef: Mapped[str] = mapped_column(String(255), primary_key=True)
    valeur: Mapped[str] = mapped_column(String(255))
