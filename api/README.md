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

## Importer des données

### Megalis

La commande suivante importe dans le répertoire ./data les [données DECP de Mégalis de 2020 à 2025](https://www.data.gouv.fr/datasets/donnees-essentielles-du-profil-acheteur-megalis-bretagne-schema-2024/) depuis la plateforme data.gouv.fr.

```bash
mkdir data && \
for url in https://www.data.gouv.fr/api/1/datasets/r/ea387298-b344-45dc-9a19-043f13df1f69 https://www.data.gouv.fr/api/1/datasets/r/3a9073a7-4062-49ff-a4b8-d4721705a462 https://www.data.gouv.fr/api/1/datasets/r/40679992-a5e7-4761-b5ba-9775e77fd133 https://www.data.gouv.fr/api/1/datasets/r/2fbb7b58-4a6b-47ca-b528-4b9dea053477 https://www.data.gouv.fr/api/1/datasets/r/da0339ac-5709-4a6b-87fa-bb9251bb371e https://www.data.gouv.fr/api/1/datasets/r/0e79013c-6764-4af4-9f2e-c757d876a666; \
do curl -L ${url} -o "data/${url: -36}.json"; done
```

L'import au sein de Focus Marchés est ensuite réalisé en appelant le script python :

```bash
python app/importation.py
```

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
