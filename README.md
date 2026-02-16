# Focus Marche v2


## A propos

Le projet Focus Marchés v2 a été développé par Numih France pour Mégalis et Recia. Il facilite l'exporation des données essentielles de la commande publique. Cette v2 est le fruit de l'évolution du schéma de données et de nouveaux besoins rapportés en ateliers UX.

Trois instances de Focus Marchés sont actuellement déployée :
- Mégalis - [focus-marches.megalis.bretagne.bzh](https://focus-marches.megalis.bretagne.bzh/)
- Arnia - [observatoire-commande-publique.arnia-bfc.fr](https://observatoire-commande-publique.arnia-bfc.fr/)
- Récia

Le projet se découpe en 2 sous-projets :
- une API et des scrips d'importation (_back_)
- une interface utilisateur (_front_)

## Licence

[CECILL-2.1](http://www.cecill.info/licences/Licence_CeCILL_V2.1-fr.html)

## Configuration et installation avec Docker

### Prérequis

Avoir installé git, docker et docker-compose.

### 1. Récupération des sources

La première étape est de récupérer le code source du projet.

```bash
git clone https://github.com/collec-data/focus-marches-v2.git
```

### 2. Configuration et personnalisation

Créer le fichier `.env`, en le recopiant depuis `.env.default` :

```bash
cp .env.default .env
```

Puis compléter le [`.env`](.env) pour configurer et personnaliser l'instance. Ci-dessous une description des paramètres importants

| Variable | Valeurs possibles | Description |
|-------|---------|------|
| MARIADB_DATA | /var/lib/mysql | |
| API_ENTREPRISE_URL | https://api.siren.do4c.sib.fr/ | Une URL d'une instance de l'API Siren |
| API_ENTREPRISE_TOKEN | | Un token d'authentification à l'API Siren |
| DATE_MIN | 2020-01-01 | La borne temporelle minimale en dessous de laquelle les données ne seront pas affichées |
| OPSN | | Le noms de l'OPSN ou de la structure qui déploie l'instance |
| REGION | | La région concernée |
| DEPARTEMENTS | 1,2,3 | Les numéros de département de la région, séparés par une virgule |
| FRONT_THEME_COLOR | amber | Une couleur parmi les suivantes : noir, emerald, green, lime, orange, amber, yellow, teal, cyan, sky, blue, indigo, violet, purple, fuchsia, pink ou rose. Cette couleur sera utilisée par défaut mais pourra toujours être modifiée ensuite par l'utilisateur. |
| SOURCES |  | Les liens permanents des fichiers annuels |

_Quelques exemples de configuration sont à retrouver tout en bas de cette page pour Mégalis, Arnia et Recia._

### 3. Création et lancement des containers docker

Construisez et lancez les container avec 
```bash
docker compose build
docker compose up -d
```

L'application est lancée et peut être explorée via un navigateur web à l'adresse [http://127.0.0.1/](http://127.0.0.1/).


_Note : La base de donnée sera persistée dans le dossier /var/lib/mysql par défaut. Il est possible de changer l'emplacement d'installation des données ou d'indiquer un emplacement d'installation existante en modifiant la variable d'environnement `MARIADB_DATA` dans le fichier .env._

### 4. Import des données

L'ultime étape est de charger les données depuis data.gouv avec les commandes suivantes.

```bash
# import des decps dont les sources ont été renseignées dans le .env
docker exec focus-marche-v2-api-1 sh -c "python app/importation.py decps --import-de-0"

# synchronisation avec l'API entreprise pour récupérer les noms et localisations de structures
docker exec focus-marche-v2-api-1 sh -c "python app/importation.py structures"
```

## Développement

La base de données peut être lancée via docker avec la commande suivante :

```bash
docker compose up db -d
```

Puis se reporter aux instructions spécifiques pour l'initialisation [du front](./front/README.md#initialisation-pour-le-développement) et [de l'API](./api/README.md#initialisation-pour-le-développement).

### Documentations spécifiques

Des documentations détaillées sont disponibles dans les dossiers suivants :

- [`api`](./api/README.md) pour le service API (back) ;
- [`front`](./front/README.md) pour l'application front.

### Tests - Statistiques
- Back ![coverage](https://gitlab.csm.ovh/focus-marches/focusmarchev2/badges/main/coverage.svg?job=api-quality)
- Front ![coverage](<https://gitlab.csm.ovh/focus-marches/focusmarchev2/badges/main/coverage.svg?job=build app>)

### Exemples de configuration

```
# Megalis 2026
...
DATE_MIN=2020-01-01
OPSN=Mégalis
REGION=Bretagne
DEPARTEMENTS=22,29,35,56
FRONT_THEME_COLOR=blue
SOURCES=https://www.data.gouv.fr/api/1/datasets/r/ea387298-b344-45dc-9a19-043f13df1f69 https://www.data.gouv.fr/api/1/datasets/r/3a9073a7-4062-49ff-a4b8-d4721705a462 https://www.data.gouv.fr/api/1/datasets/r/40679992-a5e7-4761-b5ba-9775e77fd133 https://www.data.gouv.fr/api/1/datasets/r/2fbb7b58-4a6b-47ca-b528-4b9dea053477 https://www.data.gouv.fr/api/1/datasets/r/da0339ac-5709-4a6b-87fa-bb9251bb371e https://www.data.gouv.fr/api/1/datasets/r/0e79013c-6764-4af4-9f2e-c757d876a666 https://www.data.gouv.fr/api/1/datasets/r/5b67f1cb-d8f4-491d-a15f-77cccc65456c
```

```
# Recia 2026
...
DATE_MIN=2020-01-01
OPSN=Recia
REGION=Centre-Val de Loire
DEPARTEMENTS=36,18,37,45,28,41
FRONT_THEME_COLOR=indigo
SOURCES=https://www.data.gouv.fr/api/1/datasets/r/c7b06c4e-9d31-460a-8bb3-be9caa16ff8a https://www.data.gouv.fr/api/1/datasets/r/dd24af89-7422-4a60-9a68-ceb0345ea474 https://www.data.gouv.fr/api/1/datasets/r/0a3078ea-e2eb-41be-8fd6-025054e9ee2d https://www.data.gouv.fr/api/1/datasets/r/f6af4031-e00a-4729-8525-3e6a733540d2 https://www.data.gouv.fr/api/1/datasets/r/5f0f1d6c-634f-4cb6-b502-dfe833763936 https://www.data.gouv.fr/api/1/datasets/r/79688911-246a-49e6-9401-dffe5ac2a63c https://www.data.gouv.fr/api/1/datasets/r/f9dae08d-9d65-4071-b5a7-2b8d32504ba8
```

```
# Arnia 2026
...
DATE_MIN=2020-01-01
OPSN=Arnia
REGION=Bourgogne-Franche-Comté
DEPARTEMENTS=21,71,90,58,89,39,25,70
FRONT_THEME_COLOR=orange
SOURCES=https://www.data.gouv.fr/api/1/datasets/r/f2ca0c44-ee8e-42ba-86a2-e83572c1b0d0 https://www.data.gouv.fr/api/1/datasets/r/b6e959fd-9e9d-4dfb-ba54-65b5ddf49881 https://www.data.gouv.fr/api/1/datasets/r/0647e31d-29c5-4adc-8480-23d207eec2bc https://www.data.gouv.fr/api/1/datasets/r/c9071fda-c613-4aa0-ae6a-e73dfca7ec69 https://www.data.gouv.fr/api/1/datasets/r/a136ac8f-7d5b-4bf2-b3de-7919e644aeae https://www.data.gouv.fr/api/1/datasets/r/79746469-5ba6-4955-9bb7-e5e2fdbb2472 https://www.data.gouv.fr/api/1/datasets/r/35ad0b16-c341-4d1b-a909-53f5e09d3c13
```