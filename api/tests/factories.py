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


class StructureInfogreffeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = db.StructureInfogreffe

    uid = factory.declarations.Sequence(lambda n: n)
    structure = factory.declarations.SubFactory(VendeurFactory)
    annee = factory.faker.Faker("year")
    ca = factory.faker.Faker("pyfloat")
    resultat = factory.faker.Faker("pyfloat")
    effectif = factory.faker.Faker("pyint")


class LieuFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = db.Lieu

    uid = factory.declarations.Sequence(lambda n: n)
    code = factory.declarations.Sequence(lambda n: str(n))
    type_code = enums.TypeCodeLieu.DEP.db_value


class CritereSocialFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = db.ConsiderationSocialeMarche

    uid = factory.declarations.Sequence(lambda n: n)
    consideration = enums.ConsiderationsSociales.CRITERE.db_value


class ClauseSocialeFactory(CritereSocialFactory):
    consideration = enums.ConsiderationsSociales.CLAUSE.db_value


class CritereEnvFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = db.ConsiderationEnvMarche

    uid = factory.declarations.Sequence(lambda n: n)
    consideration = enums.ConsiderationsEnvironnementales.CRITERE.db_value


class ClauseEnvFactory(CritereEnvFactory):
    consideration = enums.ConsiderationsEnvironnementales.CLAUSE.db_value


class TechniqueAchatFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = db.TechniqueAchatMarche

    uid = factory.declarations.Sequence(lambda n: n)
    technique = enums.TechniqueAchat.CONCOURS.db_value


class CPVFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = db.CPV

    code = factory.declarations.Sequence(lambda n: n)
    libelle = factory.faker.Faker("word")


class MarcheFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = db.Marche

    uid = factory.declarations.Sequence(lambda n: n)
    id = factory.declarations.Sequence(lambda n: str(n))
    acheteur = factory.declarations.SubFactory(AcheteurFactory)
    nature = enums.NatureMarche.MARCHE.db_value
    objet = "Lorem ipsum dolor"
    cpv = factory.declarations.SubFactory(CPVFactory)
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
    duree_mois_initiale = 1
    date_notification = factory.faker.Faker("date")
    montant = factory.faker.Faker("pyint")
    montant_initial = factory.faker.Faker("pyint")
    type_prix: list[enums.TypePrix] = []
    titulaires: list[VendeurFactory] = []
    considerations_sociales: list[enums.ConsiderationsSociales] = []
    considerations_environnementales: list[enums.ConsiderationsEnvironnementales] = []
    accord_cadre: MarcheFactory | None = None


class ConcessionFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = db.ContratConcession

    uid = factory.declarations.Sequence(lambda n: n)
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

    decp = "{}"
    erreurs = factory.declarations.List(
        [factory.declarations.SubFactory(ErreurFactory) for _ in range(2)]
    )
    structure = factory.declarations.SubFactory(AcheteurFactory)
    date_creation = factory.faker.Faker("date")
