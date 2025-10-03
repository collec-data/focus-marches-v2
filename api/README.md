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

## Tests

![coverage](https://gitlab.csm.ovh/focus-marches/focusmarchev2/badges/main/coverage.svg?job=api-quality)

Les tests sont situés dans le dossier (`api/tests/`). Il s'agit principalement de tests d'intégration avec des appels au niveau de l'API qui remontent jusqu'à la base de données.

On utilise pour cela [`pytest`](https://docs.pytest.org/en/stable/contents.html), associé à [`pytest-cov`](https://pytest-cov.readthedocs.io/en/latest/) pour mesurer la couverture de test, ainsi qu'à [`factoryboy`](https://factoryboy.readthedocs.io/en/stable/) pour la génération simplifiée de jeux de données de test.

Côté base de donnée, une instance docker de PostgreSQL est démarrée et gérée automatiquement par `pytest` ([`pytest-docker`](https://pypi.org/project/pytest-docker/)). Pour accélérer la vitesse d'exécution des tests, chaque test est exécuté dans une transaction et n'est jamais réellement envoyé dans le PostgreSQL (voir `tests/conftest.py::db_fixture`).

On peut les lancer manuellement à l'aide de la commande `pytest` ou via VSCode (en faisant attention d'avoir ouvert le dossier `/api` en tant que projet et non le _repository_ entier).
