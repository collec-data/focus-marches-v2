# API Focus Marche v2 (back)

[← Revenir au README général](../README.md)



## Importer des données

### Import des DECPS depuis data.gouv

Les sources sont à renseigner dans le `.env`. Il s'agit des URL stables des fichiers annuels des données essentielles de la commande publique. 

L'importation est ensuite lancée avec la commande suivante.

```bash
python app/importation.py decps
```

### Importer les données d'Infogreffe (données financières)

Les données financières des structures déjà présentes dans la base sont récupérées via l'API Datainfogreffe. Les variables `INFOGREFFE_API_KEY` et `INFOGREFFE_DATASET` doivent être renseignées dans le fichier `.env`.

```bash
python app/importation.py infogreffe
```

**Attention** : cette commande récupère les informations pour les structures présentes dans la base de données. Il faut avoir importé des DECPs avant.

### Synchroniser les noms et localisations de structures

Les noms et les localisations de structures sont récupérées depuis l'instance Numih France de l'API-Entreprise, avec la commande suivante :

```bash
python app/importation.py structures
```

**Attention** : cette commande récupère les informations pour les structures présentes dans la base de données. Il faut avoir importé des DECPs avant.

## Développement 

### Initialisation pour le développement

Pré-requis : 
- avoir installé Python (3.14).
- avoir installé les paquets `libmariadb3 libmariadb-dev` (pour Ubuntu)

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

### Tests

Les tests sont situés dans le dossier (`api/tests/`). Il s'agit principalement de tests d'intégration avec des appels au niveau de l'API qui remontent jusqu'à la base de données.

On utilise pour cela [`pytest`](https://docs.pytest.org/en/stable/contents.html), associé à [`pytest-cov`](https://pytest-cov.readthedocs.io/en/latest/) pour mesurer la couverture de test, ainsi qu'à [`factoryboy`](https://factoryboy.readthedocs.io/en/stable/) pour la génération simplifiée de jeux de données de test.

Côté base de donnée, une instance docker de PostgreSQL est démarrée et gérée automatiquement par `pytest` ([`pytest-docker`](https://pypi.org/project/pytest-docker/)). Pour accélérer la vitesse d'exécution des tests, chaque test est exécuté dans une transaction et n'est jamais réellement envoyé dans le PostgreSQL (voir `tests/conftest.py::db_fixture`).

On peut les lancer manuellement à l'aide de la commande `pytest` ou avec VSCode.
