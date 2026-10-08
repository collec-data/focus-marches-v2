import factory
from factory.alchemy import SQLAlchemyModelFactory
from factory.base import FactoryMetaClass

from app.models import db, enums


# astuce pour le typer correctement le retour des factories :
# https://github.com/FactoryBoy/factory_boy/issues/468#issuecomment-3264798657
class BaseMetaFactory[T](FactoryMetaClass):
    def __call__(cls, *_args, **kwargs) -> T:
        return super().__call__(**kwargs)


class StructureFactory(SQLAlchemyModelFactory, metaclass=BaseMetaFactory[db.Structure]):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = db.Structure

    uid = factory.declarations.Sequence(lambda n: n + 1)
    identifiant = factory.declarations.Sequence(lambda n: str(n))
    type_identifiant = "SIRET"
    vendeur = False
    acheteur = False


class AcheteurFactory(StructureFactory):
    acheteur = True


class VendeurFactory(StructureFactory):
    vendeur = True


class StructureInfogreffeFactory(
    SQLAlchemyModelFactory, metaclass=BaseMetaFactory[db.StructureInfogreffe]
):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = db.StructureInfogreffe

    uid = factory.declarations.Sequence(lambda n: n + 1)
    structure = factory.declarations.SubFactory(VendeurFactory)
    annee = factory.faker.Faker("year")
    ca = factory.faker.Faker(
        "pydecimal", right_digits=2, min_value=0, max_value=1000000000
    )
    resultat = factory.faker.Faker(
        "pydecimal", right_digits=2, min_value=-1000000000, max_value=1000000000
    )
    effectif = factory.faker.Faker("pyint")


class LieuFactory(SQLAlchemyModelFactory, metaclass=BaseMetaFactory[db.Lieu]):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = db.Lieu

    uid = factory.declarations.Sequence(lambda n: n + 1)
    code = factory.declarations.Sequence(lambda n: str(n))
    type_code = enums.TypeCodeLieu.DEP.db_value


class CritereSocialFactory(
    SQLAlchemyModelFactory, metaclass=BaseMetaFactory[db.ConsiderationSocialeMarche]
):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = db.ConsiderationSocialeMarche

    uid = factory.declarations.Sequence(lambda n: n + 1)
    consideration = enums.ConsiderationsSociales.CRITERE.db_value


class ClauseSocialeFactory(CritereSocialFactory):
    consideration = enums.ConsiderationsSociales.CLAUSE.db_value


class CritereEnvFactory(
    SQLAlchemyModelFactory, metaclass=BaseMetaFactory[db.ConsiderationEnvMarche]
):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = db.ConsiderationEnvMarche

    uid = factory.declarations.Sequence(lambda n: n + 1)
    consideration = enums.ConsiderationsEnvironnementales.CRITERE.db_value


class ClauseEnvFactory(CritereEnvFactory):
    consideration = enums.ConsiderationsEnvironnementales.CLAUSE.db_value


class TechniqueAchatFactory(
    SQLAlchemyModelFactory, metaclass=BaseMetaFactory[db.TechniqueAchatMarche]
):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = db.TechniqueAchatMarche

    uid = factory.declarations.Sequence(lambda n: n + 1)
    technique = enums.TechniqueAchat.CONCOURS.db_value


class CPVFactory(SQLAlchemyModelFactory, metaclass=BaseMetaFactory[db.CPV]):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = db.CPV

    code = factory.declarations.Sequence(lambda n: n + 1)
    libelle = factory.faker.Faker("word")


class MarcheFactory(SQLAlchemyModelFactory, metaclass=BaseMetaFactory[db.Marche]):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = db.Marche

    uid = factory.declarations.Sequence(lambda n: n + 1)
    id = factory.declarations.Sequence(lambda n: str(n))
    acheteur = factory.declarations.SubFactory(AcheteurFactory)
    nature = enums.NatureMarche.MARCHE.db_value
    objet = "Lorem ipsum dolor"
    cpv = factory.declarations.SubFactory(CPVFactory)
    categorie = enums.CategorieMarche.SERVICES.db_value
    techniques_achat = factory.declarations.LazyFunction(list)
    modalites_execution = factory.declarations.LazyFunction(list)
    marche_innovant = False
    ccag: int
    offres_recues = 1
    attribution_avance = False
    taux_avance = 0
    sous_traitance_declaree = False
    procedure = enums.ProcedureMarche.ADAPTE.db_value
    lieu = factory.declarations.SubFactory(LieuFactory)
    duree_mois = 1
    duree_mois_initiale = 1
    date_notification = factory.faker.Faker("date")
    montant = factory.faker.Faker(
        "pydecimal", right_digits=2, min_value=0, max_value=1000000000
    )
    montant_initial = factory.faker.Faker(
        "pydecimal", right_digits=2, min_value=0, max_value=1000000000
    )
    type_prix = factory.declarations.LazyFunction(list)
    titulaires = factory.declarations.LazyFunction(list)
    considerations_sociales = factory.declarations.LazyFunction(list)
    considerations_environnementales = factory.declarations.LazyFunction(list)
    accord_cadre: MarcheFactory | None = None


class ConcessionFactory(
    SQLAlchemyModelFactory, metaclass=BaseMetaFactory[db.ContratConcession]
):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = db.ContratConcession

    uid = factory.declarations.Sequence(lambda n: n + 1)
    id = factory.declarations.Sequence(lambda n: str(n))
    autorite_concedante = factory.declarations.SubFactory(AcheteurFactory)
    objet = "Lorem ipsum dolor"
    procedure = enums.ProcedureConcession.NEGO_OUVERTE.db_value
    duree_mois = 1
    duree_mois_initiale = 1
    date_signature = factory.faker.Faker("date")
    date_publication = factory.faker.Faker("date")
    date_debut_execution = factory.faker.Faker("date")
    valeur_globale = factory.faker.Faker("pyint")
    valeur_globale_initiale = factory.faker.Faker("pyint")
    montant_subvention_publique = 0.0
    considerations_sociales = factory.declarations.LazyFunction(list)
    considerations_environnementales = factory.declarations.LazyFunction(list)
    concessionnaires = factory.declarations.LazyFunction(list)


class ErreurFactory(SQLAlchemyModelFactory, metaclass=BaseMetaFactory[db.Erreur]):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = db.Erreur

    type = "Erreur générique"
    localisation = "."
    message = "Lorem ipsum dolor"


class DecpMalFormeFactory(
    SQLAlchemyModelFactory, metaclass=BaseMetaFactory[db.DecpMalForme]
):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = db.DecpMalForme

    decp = "{}"
    erreurs = factory.declarations.List(
        [factory.declarations.SubFactory(ErreurFactory) for _ in range(2)]
    )
    structure = factory.declarations.SubFactory(AcheteurFactory)
    date_creation = factory.faker.Faker("date")


class ConfFactory(SQLAlchemyModelFactory, metaclass=BaseMetaFactory[db.Conf]):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = db.Conf

    clef = factory.faker.Faker("string")
    valeur = factory.faker.Faker("string")
