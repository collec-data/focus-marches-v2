from enum import StrEnum


class CustomStrEnum(StrEnum):
    db_value: int

    # https://docs.python.org/3/howto/enum.html#when-to-use-new-vs-init
    def __new__(cls, value, db_value):
        obj = str.__new__(cls, [value])
        obj._value_ = value
        obj.db_value = db_value
        return obj


class NatureMarche(CustomStrEnum):
    MARCHE = "Marché", 1
    PARTENARIAT = "Marché de partenariat", 2
    DEFSEC = "Marché de défense ou de sécurité", 3


class ProcedureMarche(CustomStrEnum):
    ADAPTE = "Procédure adaptée", 1
    AO_OUVERT = "Appel d'offres ouvert", 2
    AO_RESTREINT = "Appel d'offres restreint", 3
    SANS_PUB = "Marché passé sans publicité ni mise en concurrence préalable", 4
    COMPETITIF = "Dialogue compétitif", 5
    NEGO = "Procédure avec négociation", 6


class CCAG(CustomStrEnum):
    TRAVAUX = "Travaux", 1
    MO = "Maitrise d'œuvre", 2
    FOURNITURE = "Fournitures courantes et services", 3
    INDUS = "Marchés industriels", 4
    PRESTA = "Prestations intellectuelles", 5
    TIC = "Techniques de l'information et de la communication", 6
    AUCUN = "Pas de CCAG", None


class TypeGroupementOperateur(CustomStrEnum):
    CONJOINT = "Conjoint", 1
    SOLIDAIRE = "Solidaire", 2
    AUCUN = "Pas de groupement", None


class TypePrix(CustomStrEnum):
    FERME = "Définitif ferme", 1
    ACTUALISABLE = "Définitif actualisable", 2
    REVISABLE = "Définitif révisable", 3
    PROVISOIRE = "Provisoire", 4


class FormePrix(CustomStrEnum):
    UNITAIRE = "Unitaire", 1
    FORFAITAIRE = "Forfaitaire", 2
    MIXTE = "Mixte", 3


class VariationPrix(CustomStrEnum):
    FERME = "Ferme", 1
    ACTUALISABLE = "Actualisable", 2
    REVISABLE = "Révisable", 3
    NC = "NC", None


class ConsiderationsSociales(CustomStrEnum):
    CRITERE = "Critère social", 1
    CLAUSE = "Clause sociale", 2
    MARCHE_RESERVE = "Marché réservé", 3
    CONCESSION_RESERVE = "Concession réservé", 4
    AUCUNE = "Pas de considération sociale", None


class ConsiderationsEnvironnementales(CustomStrEnum):
    CRITERE = "Critère environnemental", 1
    CLAUSE = "Clause environnementale", 2
    AUCUNE = "Pas de considération environnementale", None


class NatureConcession(CustomStrEnum):
    TRAVAUX = "Concession de travaux", 1
    SERVICE = "Concession de service", 2
    SERVICE_PUBLIC = "Concession de service public", 3
    DELEGATION = "Délégation de service public", 4


class ProcedureConcession(CustomStrEnum):
    NEGO_OUVERTE = "Procédure négociée ouverte", 1
    NON_NEGO_OUVERTE = "Procédure non négociée ouverte", 2
    NEGO_RESTREINTE = "Procédure négociée restreinte", 3
    NON_NEGO_RESTREINTE = "Procédure non négociée restreinte", 4


class TechniqueAchat(CustomStrEnum):
    AC = "Accord-cadre", 1
    CONCOURS = "Concours", 2
    QUALIF = "Système de qualification", 3
    ACQUISITION_DYNAMIQUE = "Système d'acquisition dynamique", 4
    CATALOGUE = "Catalogue électronique", 5
    ENCHERE = "Enchère électronique", 6
    SANS_OBJET = "Sans objet", None


class ModaliteExecution(CustomStrEnum):
    MARCHE_TRANCHES = "Tranches", 1
    BON_COMMANDE = "Bons de commande", 2
    MARCHE_SUBSEQUENT = "Marchés subséquents", 3
    SANS_OBJET = "Sans objet", None


class IdentifiantStructure(StrEnum):
    SIRET = "SIRET"
    TVA = "TVA"
    TAHITI = "TAHITI"
    RIDET = "RIDET"
    FRWF = "FRWF"
    IREP = "IREP"
    UE = "UE"
    HORSUE = "HORS-UE"


class TypeCodeLieu(CustomStrEnum):
    POSTAL = "Code postal", 1
    COMMUNE = "Code commune", 2
    ARRONDISSEMENT = "Code arrondissement", 3
    CANTON = "Code canton", 4
    DEP = "Code département", 5
    REGION = "Code région", 6
    PAYS = "Code pays", 7
