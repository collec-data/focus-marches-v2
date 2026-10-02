# Focus Marche

Plateforme de consultation des données d'achat des collectivités : marchés, concessions et indicateurs associées à un acheteur public. Ce glossaire fixe le vocabulaire du domaine et distingue ce qui est **connu** de ce qui ne l'est pas encore — distinction qui traverse toute l'interface.

## Structures

**Structure**:
Tout organisme identifié dans la base, acheteur, vendeur, ou les deux.
_Avoid_ : société, entreprise, organisme, compte

**Acheteur**:
Structure qui passe des marchés.
_Avoid_ : client, utilisateur, demandeur

**Vendeur**:
Structure qui répond à des marchés, titulaire d'un ou de plusieurs marchés.
_Avoid_ : fournisseur, prestataire, attributaire

**Autorité concedante**:
Acheteur qui délègue un service public par voie de concession.
_Avoid_ : acheteur, délégataire

**Concessionnaire**:
Vendeur qui exploite un service public délégué par concession.
_Avoid_ : titulaire, attributaire, autorité

**SIRET**:
Identifiant à 14 chiffres portant le numéro d'immatriculation d'une structure. C'est la forme sous laquelle un acheteur est désigné publiquement, en particulier dans les liens et les pages intégrables.
_Avoid_ : identifiant, id, numéro, code

## Filtres

**Filtre**:
Critère restreignant un agrégat à un sous-ensemble des données de la plateforme.
_Avoid_ : critère, condition, paramètre de recherche

**Aucun filtre**:
Un agrégat calculé sur l'ensemble de la plateforme, faute de restriction. C'est un résultat **légitime et volontaire** : l'utilisateur a choisi de ne rien restreindre.
_Avoid_ : tout, sans filtre, global

**Période de référence**:
Fenêtre de dates sur laquelle un agrégat est calculé, exprimée en mois. Un agrégat sans période n'a pas de durée associée.
_Avoid_ : période, dates, fenêtre temporelle, intervalle

**Indicateurs**:
Valeurs agrégées d'un acheteur sur une période et un ensemble de filtres : nombre de contrats, montant total, nombre d'acheteurs, nombre de fournisseurs, etc.

## Surfaces de restitution

**Tableau de bord**:
Page interne regroupant l'ensemble des indicateurs d'un acheteur, dans l'application.
_Avoid_ : dashboard, page acheteur, fiche

**Widget**:
Fragment intégrable individuellement sur le site d'un acheteur au moyen d'un cadre tiers. Il restitue une partie restreinte des indicateurs d'un seul acheteur, désigné par son SIRET.
_Avoid_ : iframe, module, bloc, widget public
