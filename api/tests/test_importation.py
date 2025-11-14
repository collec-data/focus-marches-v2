from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import select

from app.importation import ImportateurDecp
from app.models.db import ContratConcession, DecpMalForme, Marche
from app.models.enums import TypeCodeLieu
from tests.factories import LieuFactory


def test_cast_jour():
    i = ImportateurDecp(None, preload_db=False)
    assert i.cast_jour("2020-05-15") == datetime(2020, 5, 15)


def test_get_or_create_lieu(db):
    existing_lieu = LieuFactory.create(type_code=TypeCodeLieu.COMMUNE.db_value)

    i = ImportateurDecp(db)

    lieu1 = i.get_or_create_lieu("35", TypeCodeLieu.DEP)  # nouveau lieu créé
    lieu2 = i.get_or_create_lieu("35", TypeCodeLieu.DEP)  # @cache utilisé
    assert lieu1 == lieu2

    lieu3 = i.get_or_create_lieu(
        existing_lieu.code, TypeCodeLieu.COMMUNE
    )  # pré-chargé dans le cache
    assert lieu3 == existing_lieu


def test_importation_marche_succes(db):
    i = ImportateurDecp(session=db)
    i.importer_marches(file="tests/files/liste_marches_valides.json")

    marches_crees = list(db.execute(select(Marche)).scalars())
    assert len(marches_crees) == 3

    # `marche1` est un exemple avec tous les champs existants remplis
    # On s'assure que toutes les données sont bien utilisées et retrouvées ensuite dans la BDD
    marche1 = marches_crees[0]
    assert marche1.id == "2021T00000"
    assert marche1.acheteur.identifiant == "13579135791357"
    assert marche1.acheteur.type_identifiant == "SIRET"
    assert marche1.acheteur.vendeur is False
    assert marche1.acheteur.acheteur is True
    assert marche1.nature == 1
    assert marche1.objet == "Lorem ipsum dolor"
    assert marche1.cpv == "12341234"
    assert marche1.techniques_achat == []
    assert marche1.modalites_execution == []
    assert marche1.marche_innovant is True
    assert marche1.ccag == 1
    assert marche1.offres_recues == 5
    assert marche1.attribution_avance is True
    assert marche1.taux_avance == 0.5
    assert marche1.type_groupement_operateurs is None
    assert marche1.sous_traitance_declaree is True
    assert marche1.procedure == 5
    assert marche1.lieu.code == "35"
    assert marche1.lieu.type_code == 5
    assert marche1.duree_mois == 11
    assert marche1.duree_mois_initiale == 99
    assert marche1.date_notification == date(2042, 12, 1)
    assert marche1.date_publication == date(2042, 12, 2)
    assert marche1.montant == Decimal(11111.0)
    assert marche1.montant_initial == 6.66e7
    assert marche1.type_prix == [3]
    assert marche1.forme_prix == 2
    assert len(marche1.titulaires) == 1
    assert marche1.titulaires[0].identifiant == "12345678991230"
    assert marche1.titulaires[0].type_identifiant == "SIRET"
    assert marche1.considerations_sociales == []
    assert len(marche1.considerations_environnementales)
    assert marche1.considerations_environnementales[0].consideration == 1
    assert len(marche1.modifications) == 2
    assert marche1.modifications[0].id == 1
    assert marche1.modifications[0].date_notification == date(2025, 1, 1)
    assert marche1.modifications[0].date_publication == date(2025, 1, 2)
    assert marche1.modifications[0].montant == Decimal("3027.97")
    assert len(marche1.modifications[0].titulaires) == 1
    assert marche1.modifications[0].titulaires[0].identifiant == "12345678991230"
    assert marche1.modifications[0].titulaires[0].type_identifiant == "SIRET"
    assert marche1.modifications[0].titulaires[0].acheteur is False
    assert marche1.modifications[0].titulaires[0].vendeur is True
    assert len(marche1.actes_sous_traitance) == 1
    assert marche1.actes_sous_traitance[0].id == 1010
    assert marche1.actes_sous_traitance[0].sous_traitant.identifiant == "12365478962145"
    assert marche1.actes_sous_traitance[0].sous_traitant.type_identifiant == "SIRET"
    assert marche1.actes_sous_traitance[0].date_notification == date(2025, 6, 1)
    assert marche1.actes_sous_traitance[0].date_publication == date(2025, 6, 3)
    assert marche1.actes_sous_traitance[0].montant == Decimal("5.9E7")
    assert marche1.actes_sous_traitance[0].duree_mois == 20
    assert marche1.actes_sous_traitance[0].variation_prix == 2
    assert len(marche1.actes_sous_traitance[0].modifications) == 2
    assert marche1.actes_sous_traitance[0].modifications[0].duree_mois == 10
    assert marche1.actes_sous_traitance[0].modifications[0].date_notif == date(
        2025, 7, 1
    )
    assert marche1.actes_sous_traitance[0].modifications[0].date_publication == date(
        2025, 7, 3
    )
    assert marche1.actes_sous_traitance[0].modifications[0].montant == Decimal("5.86E7")

    # marche2 est un exemple du strict minimum de champs remplis
    marche1 = marches_crees[1]


def test_importation_concession_succes(db):
    i = ImportateurDecp(session=db)
    i.importer_concessions(file="tests/files/liste_concessions_valides.json")

    concessions_crees = list(db.execute(select(ContratConcession)).scalars())
    assert len(concessions_crees) == 2

    # `concession1` est un exemple avec tous les champs existants remplis
    # On s'assure que toutes les données sont bien utilisées et retrouvées ensuite dans la BDD
    concession1 = concessions_crees[0]
    assert concession1.id == "2025S00001"
    assert concession1.autorite_concedante.identifiant == "12345678912345"
    assert concession1.autorite_concedante.type_identifiant == "SIRET"
    assert concession1.autorite_concedante.acheteur is True
    assert concession1.autorite_concedante.vendeur is False
    assert concession1.nature == 2
    assert concession1.objet == "Lorem ipsum dolor"
    assert concession1.procedure == 2
    assert concession1.duree_mois == 150
    assert concession1.duree_mois_initiale == 180
    assert concession1.date_signature == date(2025, 1, 10)
    assert concession1.date_publication == date(2025, 2, 1)
    assert concession1.date_debut_execution == date(2025, 3, 1)
    assert concession1.valeur_globale == Decimal("4000.0")
    assert concession1.valeur_globale_initiale == Decimal("31987.0")
    assert concession1.montant_subvention_publique == 0
    assert len(concession1.concessionnaires) == 1
    assert concession1.concessionnaires[0].identifiant == "12398755624565"
    assert concession1.concessionnaires[0].type_identifiant == "SIRET"
    assert concession1.concessionnaires[0].vendeur is True
    assert concession1.concessionnaires[0].acheteur is False
    assert concession1.considerations_sociales == []
    assert concession1.considerations_environnementales == []
    assert len(concession1.donnees_execution) == 1
    assert concession1.donnees_execution[0].date_publication == date(2025, 1, 1)
    assert concession1.donnees_execution[0].depenses_investissement == Decimal("100000")
    assert len(concession1.donnees_execution[0].tarifs) == 2
    assert concession1.donnees_execution[0].tarifs[0].intitule == "1 voyage"
    assert concession1.donnees_execution[0].tarifs[0].tarif == Decimal(1)
    assert len(concession1.modifications) == 1
    assert concession1.modifications[0].id == 1
    assert concession1.modifications[0].date_signature == date(2025, 5, 1)
    assert concession1.modifications[0].date_publication == date(2025, 5, 10)
    assert concession1.modifications[0].valeur_globale == Decimal(4000)


def test_importation_erreur(db):
    i = ImportateurDecp(session=db)
    i.importer_marches(file="tests/files/liste_pour_erreurs.json")

    decp_mal_formes = list(db.execute(select(DecpMalForme)).scalars())
    assert len(decp_mal_formes) == 1
    assert len(decp_mal_formes[0].erreurs) > 0
