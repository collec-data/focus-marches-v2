# API Focus Marche v2 (back)

[← Revenir au README général](../README.md)

## Importer des données

### Import des DECPS depuis data.gouv

Les sources sont à renseigner dans le `.env`. Il s'agit des URL stables des fichiers annuels des données essentielles de la commande publique. 

L'importation est ensuite lancée avec la commande suivante.

```bash
docker compose exec api sh -c "python app/importation.py decps"
```

### Importer les données d'Infogreffe (données financières)

La première étape est de créer un token api sur le site datainfogreffe.
La liste des jeux de données est disponible à cette adresse [https://opendata.datainfogreffe.fr/explore/assets/chiffres-cles-2024/](https://opendata.datainfogreffe.fr/explore/assets/chiffres-cles-2024/).
Une inscription (gratuite) est nécessaire pour pouvoir creer un token.
Il faut ajouter les variables `INFOGREFFE_API_KEY` et `INFOGREFFE_DATASET` dans le `.env`.
L'import est ensuite lancé avec la commande suivante.

```bash
docker compose exec api sh -c "python app/importation.py infogreffe"
```

```bash
uv run python app/importation.py infogreffe
```

**Attention** : cette commande récupère les informations pour les structures présentes dans la base de données. Il faut avoir importé des DECPs avant.

### Synchroniser les noms et localisations de structures

Les noms et les localisations de structures sont récupérées depuis l'instance Numih France de l'API-Entreprise, avec la commande suivante :

```bash
docker compose exec api sh -c "python app/importation.py structures"
```

**Attention** : cette commande récupère les informations pour les structures présentes dans la base de données. Il faut avoir importé des DECPs avant.

## Comparer un profil acheteur au consolidé national

La commande `comparaison_annuelle` vérifie, pour une année de notification donnée, que les
marchés publiés par un profil acheteur (OPSN) se retrouvent bien dans le fichier consolidé
national de la DAJ.

```bash
uv run python app/comparaison_annuelle.py comparer --annee 2024
```

Les fichiers sont téléchargés depuis data.gouv via les URL stables `/api/1/datasets/r/<id>`
(les URL `static.data.gouv.fr` sont versionnées et disparaissent), puis conservés dans
`./decp-cache`. Le nom de cache porte la date de mise à jour de la ressource : une version
plus récente remplace l'ancienne, et `--rafraichir` force le retéléchargement.

Deux rapports sont produits dans `./rapports` :

- `comparaison-<annee>.csv` : une ligne par marché unifié. La colonne `perimetre` distingue
  les marchés de l'OPSN (`megalis`), ceux du national sans contrepartie (`daj_seul`) et ceux
  dont la date de notification est inexploitable (`anomalie`). Les manquants sont triés en
  tête, suivis des marchés appariés présentant un écart.
- `synthese-<annee>.csv` : taux de couverture par SIRET acheteur.

Quelques particularités des sources, qui expliquent la forme de l'outil :

- Seul `decp-global.json` est utilisé côté national. Les fichiers annuels de la DAJ ne
  partitionnent ni par date de notification ni par date de publication.
- Tous les fichiers annuels de l'OPSN sont lus, car un marché notifié en année N peut être
  publié dans le fichier d'une autre année.
- Le périmètre des acheteurs est déduit des fichiers de l'OPSN, sans liste à maintenir.
- L'appariement se fait en cascade : clé `(acheteur, id)`, puis acheteur, date de
  notification et titulaire commun. Le niveau retenu figure dans le rapport.
- Le consolidé national republie certains marchés plusieurs fois : ils sont dédoublonnés sur
  la clé `(acheteur, id)` et le nombre d'occurrences est reporté.

## Développement 

### Initialisation pour le développement

Pré-requis : 
- avoir installé Python (3.14).
- avoir installé les paquets `libmariadb3 libmariadb-dev` (pour Ubuntu)

Depuis le dossier courant (`api`) :

```shell
# initialiser le virtualenv et installer les dépendances :
uv sync
```

Utiliser Visual Studio Code et installer les extensions recommandées (extension Python).

### Lancer l'API en local

```bash
uv run fastapi dev
```

### Gérer les versions des dépendances

Les dépendances sont à gérer dans le fichier [api/pyproject.toml](api/pyproject.toml).

`uv` fournit des commandes pour faciliter la gestion des dépendances. Voir la documentation : https://docs.astral.sh/uv/concepts/projects/dependencies/.

Après une mise à jour de version ou un ajout de dépendance dans le fichier [`pyproject.toml`](./pyproject.toml), les paquets peuvent être installés manuellement en lançant `uv sync`.

Le lancement d'une commande avec `uv run` se chargera automatiquement de cette étape. 

Le fichier `uv.lock` liste les dépendances directes et transitives avec leurs versions (pour la reproductibilité des builds). Il est généré par `uv` lors de l'installation des dépendances.

### Tests

Les tests sont situés dans le dossier (`api/tests/`). Il s'agit principalement de tests d'intégration avec des appels au niveau de l'API qui remontent jusqu'à la base de données.

On utilise pour cela [`pytest`](https://docs.pytest.org/en/stable/contents.html), associé à [`pytest-cov`](https://pytest-cov.readthedocs.io/en/latest/) pour mesurer la couverture de test, ainsi qu'à [`factoryboy`](https://factoryboy.readthedocs.io/en/stable/) pour la génération simplifiée de jeux de données de test.

Côté base de donnée, une instance docker de PostgreSQL est démarrée et gérée automatiquement par `pytest` ([`pytest-docker`](https://pypi.org/project/pytest-docker/)). Pour accélérer la vitesse d'exécution des tests, chaque test est exécuté dans une transaction et n'est jamais réellement envoyé dans le PostgreSQL (voir `tests/conftest.py::db_fixture`).

On peut les lancer manuellement à l'aide de la commande `uv run pytest` ou avec VSCode.
