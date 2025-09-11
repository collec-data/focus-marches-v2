import factory

from app.models import db, enums


class StructureFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = db.Structure

    uid = factory.Sequence(lambda n: n)
    identifiant = factory.Sequence(lambda n: str(n))
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

    uid = factory.Sequence(lambda n: n)
    code = factory.Sequence(lambda n: str(n))
    type_code = "Code Générique"


class MarcheFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = db.Marche

    uid = factory.Sequence(lambda n: n)
    id = factory.Sequence(lambda n: n)
    acheteur = factory.SubFactory(AcheteurFactory)
    nature = "Marché"
    objet = "Lorem ipsum dolor"
    cpv = "1234"
    techniques_achat: list[enums.TechniqueAchat] = []
    modalites_execution: list[enums.ModaliteExecution] = []
    marche_innovant = False
    offres_recues = 1
    attribution_avance = False
    taux_avance = 0
    sous_traitance_declaree = False
    lieu = factory.SubFactory(LieuFactory)
    duree_mois = 1
    date_notification = factory.Faker("date_time")
    montant = factory.Faker("pyint")
    type_prix: list[enums.TypePrix] = []
    considerations_sociales: list[enums.ConsiderationsSociales] = []
    considerations_environnementales: list[enums.ConsiderationsEnvironnementales] = []


class ConcessionFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = db.ContratConcession

    uid = factory.Sequence(lambda n: n)
    id = factory.Sequence(lambda n: n)
    autorite_concedante = factory.SubFactory(AcheteurFactory)
    objet = "Lorem ipsum dolor"
    procedure = enums.ProcedureConcession.NEGO_OUVERTE.value
    duree_mois = 1
    date_signature = factory.Faker("date_time")
    date_publication = factory.Faker("date_time")
    date_debut_execution = factory.Faker("date_time")
    valeur_globale = factory.Faker("pyint")
    montant_subvention_publique = 0.0
    considerations_sociales: list[enums.ConsiderationsSociales] = []
    considerations_environnementales: list[enums.ConsiderationsEnvironnementales] = []
