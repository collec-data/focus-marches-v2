import factory

from app.models import db, enums


class StructureFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = db.Structure

    uid = factory.declarations.Sequence(lambda n: n)
    identifiant = factory.declarations.Sequence(lambda n: str(n))
    type_identifiant = "SIRET"
    vendeur = False
    acheteur = False


class AcheteurFactory(StructureFactory):
    acheteur = True


class VendeurFactory(StructureFactory):
    vendeur = True


class LieuFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = db.Lieu

    uid = factory.declarations.Sequence(lambda n: n)
    code = factory.declarations.Sequence(lambda n: str(n))
    type_code = enums.TypeCodeLieu.DEP.db_value


class MarcheFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = db.Marche

    uid = factory.declarations.Sequence(lambda n: n)
    id = factory.declarations.Sequence(lambda n: str(n))
    acheteur = factory.declarations.SubFactory(AcheteurFactory)
    nature = enums.NatureMarche.MARCHE.db_value
    objet = "Lorem ipsum dolor"
    cpv = "1234"
    categorie = enums.CategorieMarche.SERVICES.db_value
    techniques_achat: list[enums.TechniqueAchat] = []
    modalites_execution: list[enums.ModaliteExecution] = []
    marche_innovant = False
    ccag: int
    offres_recues = 1
    attribution_avance = False
    taux_avance = 0
    sous_traitance_declaree = False
    procedure = enums.ProcedureMarche.ADAPTE.db_value
    lieu = factory.declarations.SubFactory(LieuFactory)
    duree_mois = 1
    date_notification = factory.faker.Faker("date")
    montant = factory.faker.Faker("pyint")
    type_prix: list[enums.TypePrix] = []
    titulaires: list[VendeurFactory] = []
    considerations_sociales: list[enums.ConsiderationsSociales] = []
    considerations_environnementales: list[enums.ConsiderationsEnvironnementales] = []


class ConcessionFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = db.ContratConcession

    uid = factory.declarations.Sequence(lambda n: n)
    id = factory.declarations.Sequence(lambda n: str(n))
    autorite_concedante = factory.declarations.SubFactory(AcheteurFactory)
    objet = "Lorem ipsum dolor"
    procedure = enums.ProcedureConcession.NEGO_OUVERTE.db_value
    duree_mois = 1
    date_signature = factory.faker.Faker("date")
    date_publication = factory.faker.Faker("date")
    date_debut_execution = factory.faker.Faker("date")
    valeur_globale = factory.faker.Faker("pyint")
    montant_subvention_publique = 0.0
    considerations_sociales: list[enums.ConsiderationsSociales] = []
    considerations_environnementales: list[enums.ConsiderationsEnvironnementales] = []
    concessionnaires: list[VendeurFactory] = []


class ErreurFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = db.Erreur

    type = "Erreur générique"
    localisation = "."
    message = "Lorem ipsum dolor"


class DecpMalFormeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = db.DecpMalForme

    decp = factory.declarations.LazyFunction(list)
    erreurs = factory.declarations.List(
        [factory.declarations.SubFactory(ErreurFactory) for _ in range(2)]
    )
