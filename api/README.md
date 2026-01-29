# API Focus Marche v2 (back)

[← Revenir au README général](../README.md)

## Initialisation pour le développement

Pré-requis : avoir installé Python (3.12).

Depuis le dossier courant (`api`) :

```shell
# initialiser le virtualenv
python3 -m venv .venv
source .venv/bin/activate

# installer les dépendances :
pip install -r dev-requirements.txt
pip install pip-tools
```

Utiliser Visual Studio Code et installer les extensions recommandées (extension Python).


Il peut être nécessaire d'installer le paquet mariadb sur sa machine
```
sudo apt install libmariadb3 libmariadb-dev
```

## Importer des données

### Import des DECPS depuis data.gouv

Les fichiers sont à télécharger et à déplacer dans le dossier `api/data`. Si besoin le créer avec la commande `mkdir data`. Il suffit ensuite d'exécuter, depuis `api/`, la commande correspondant au profil acheteur.

L'import au sein de Focus Marchés est ensuite réalisé en appelant le script python :

```bash
python app/importation.py decps
```

#### [Megalis](https://www.data.gouv.fr/datasets/donnees-essentielles-du-profil-acheteur-megalis-bretagne-schema-2024/)

```bash
for url in https://www.data.gouv.fr/api/1/datasets/r/ea387298-b344-45dc-9a19-043f13df1f69 https://www.data.gouv.fr/api/1/datasets/r/3a9073a7-4062-49ff-a4b8-d4721705a462 https://www.data.gouv.fr/api/1/datasets/r/40679992-a5e7-4761-b5ba-9775e77fd133 https://www.data.gouv.fr/api/1/datasets/r/2fbb7b58-4a6b-47ca-b528-4b9dea053477 https://www.data.gouv.fr/api/1/datasets/r/da0339ac-5709-4a6b-87fa-bb9251bb371e https://www.data.gouv.fr/api/1/datasets/r/0e79013c-6764-4af4-9f2e-c757d876a666 https://www.data.gouv.fr/api/1/datasets/r/5b67f1cb-d8f4-491d-a15f-77cccc65456c; \
do curl -L ${url} -o "data/${url: -36}.json"; done
```

#### [ARNIA](https://www.data.gouv.fr/datasets/donnees-essentielles-du-profil-acheteur-arnia-1/)

```bash
for url in https://www.data.gouv.fr/api/1/datasets/r/f2ca0c44-ee8e-42ba-86a2-e83572c1b0d0 https://www.data.gouv.fr/api/1/datasets/r/b6e959fd-9e9d-4dfb-ba54-65b5ddf49881 https://www.data.gouv.fr/api/1/datasets/r/0647e31d-29c5-4adc-8480-23d207eec2bc https://www.data.gouv.fr/api/1/datasets/r/c9071fda-c613-4aa0-ae6a-e73dfca7ec69 https://www.data.gouv.fr/api/1/datasets/r/a136ac8f-7d5b-4bf2-b3de-7919e644aeae https://www.data.gouv.fr/api/1/datasets/r/79746469-5ba6-4955-9bb7-e5e2fdbb2472 https://www.data.gouv.fr/api/1/datasets/r/35ad0b16-c341-4d1b-a909-53f5e09d3c13; \
do curl -L ${url} -o "data/${url: -36}.json"; done
```

#### [RECIA](https://www.data.gouv.fr/datasets/donnees-essentielles-du-profil-acheteur-gip-recia/)
```bash
for url in https://www.data.gouv.fr/api/1/datasets/r/c7b06c4e-9d31-460a-8bb3-be9caa16ff8a https://www.data.gouv.fr/api/1/datasets/r/dd24af89-7422-4a60-9a68-ceb0345ea474 https://www.data.gouv.fr/api/1/datasets/r/0a3078ea-e2eb-41be-8fd6-025054e9ee2d https://www.data.gouv.fr/api/1/datasets/r/f6af4031-e00a-4729-8525-3e6a733540d2 https://www.data.gouv.fr/api/1/datasets/r/5f0f1d6c-634f-4cb6-b502-dfe833763936 https://www.data.gouv.fr/api/1/datasets/r/79688911-246a-49e6-9401-dffe5ac2a63c https://www.data.gouv.fr/api/1/datasets/r/f9dae08d-9d65-4071-b5a7-2b8d32504ba8; \
do curl -L ${url} -o "data/${url: -36}.json"; done
```


#### [Fichiers consolidés nationnal annuel](https://www.data.gouv.fr/datasets/donnees-essentielles-de-la-commande-publique-fichiers-consolides/)
```bash
for url in https://www.data.gouv.fr/api/1/datasets/r/d00a6a5a-beef-442e-8aee-5867f47a87d0 https://www.data.gouv.fr/api/1/datasets/r/4fafdaff-b697-4494-9523-e9f56916fea8 https://www.data.gouv.fr/api/1/datasets/r/59ba0edb-cf94-4bf1-a546-61f561553917 https://www.data.gouv.fr/api/1/datasets/r/16962018-5c31-4296-9454-5998585496d2  ; \
do curl -L ${url} -o "data/${url: -36}.json"; done
```

### Importer les données d'infogreffe (données financières)

La première étape est de récupérer le dernier jeu de données au format JSON depuis le site datainfogreffe. La liste des jeux de données est disponible à cette adresse [https://opendata.datainfogreffe.fr/explore/assets/chiffres-cles-2024/](https://opendata.datainfogreffe.fr/explore/assets/chiffres-cles-2024/). Une inscription (gratuite) est nécessaire pour pouvoir télécharger le fichier.

```bash
python app/importation.py infogreffe {le_chemin_du_fichier}
```

**Attention** : cette commande récupère les informations pour les structures présentes dans la base de données. Il faut avoir importé des DECPs avant.

### Synchroniser les noms et localisations de structures

Les noms et les localisations de structures sont récupérées depuis l'instance Numih France de l'API-Entreprise, avec la commande suivante :

```bash
python app/importation.py structures
```

**Attention** : cette commande récupère les informations pour les structures présentes dans la base de données. Il faut avoir importé des DECPs avant.

## Tâches courantes

### Lancer l'API en local

```bash
fastapi dev
```

### Epingler les versions des dépendances

Les fichiers (générés) `requirements.txt` et `dev-requirements.txt` listent les dépendances directes et transitives avec leurs versions (pour la reproductibilité des builds).

Ces fichiers ne sont pas à modifier manuellement, les dépendances sont à gérer dans le fichier [api/pyproject.toml](api/pyproject.toml).

Après une mise à jour de version ou un ajout de dépendance dans le `pyproject.toml`, re-générer les requirements :

```shell
pip-compile pyproject.toml -o requirements.txt  && \
  pip-compile pyproject.toml --extra dev -o dev-requirements.txt

# Ne pas oublier ensuite de réinstaller les dépendances.
pip install -r dev-requirements.txt
```

## Tests ![coverage](https://gitlab.csm.ovh/focus-marches/focusmarchev2/badges/main/coverage.svg?job=api-quality)

Les tests sont situés dans le dossier (`api/tests/`). Il s'agit principalement de tests d'intégration avec des appels au niveau de l'API qui remontent jusqu'à la base de données.

On utilise pour cela [`pytest`](https://docs.pytest.org/en/stable/contents.html), associé à [`pytest-cov`](https://pytest-cov.readthedocs.io/en/latest/) pour mesurer la couverture de test, ainsi qu'à [`factoryboy`](https://factoryboy.readthedocs.io/en/stable/) pour la génération simplifiée de jeux de données de test.

Côté base de donnée, une instance docker de PostgreSQL est démarrée et gérée automatiquement par `pytest` ([`pytest-docker`](https://pypi.org/project/pytest-docker/)). Pour accélérer la vitesse d'exécution des tests, chaque test est exécuté dans une transaction et n'est jamais réellement envoyé dans le PostgreSQL (voir `tests/conftest.py::db_fixture`).

On peut les lancer manuellement à l'aide de la commande `pytest` ou avec VSCode.
