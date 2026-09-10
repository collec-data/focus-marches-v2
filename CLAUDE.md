# focusmarchev2

Monorepo : `api/` (FastAPI, Python 3.14) et `front/` (Vue 3, Vite, TypeScript).
CI GitLab : `.gitlab-ci.yml` inclut `api/.gitlab-ci.yml` (job `api-quality`) et
`front/.gitlab-ci.yml` (job `build app`).

## Vérifications à faire AVANT chaque commit

Ne jamais commiter sans avoir rejoué localement les commandes du job CI
correspondant. Un seul échec parmi elles casse le build.

### Si `api/` est modifié — reproduit le job `api-quality`

```bash
cd api
source .venv/bin/activate        # ou utiliser .venv/bin/<outil> directement
pytest                           # les tests utilisent testcontainers => Docker requis
ruff format --check .            # sinon : ruff format .
ruff check .                     # sinon : ruff check --fix .
mypy . --strict                  # AUCUNE erreur tolérée, le job échoue sinon
```

Points d'attention `mypy --strict` :

- toute annotation générique doit être paramétrée : `dict[str, Any]`, jamais `dict` nu ;
- toute fonction doit être annotée (paramètres **et** retour) ;
- un module tiers non typé qui ré-exporte ses symboles sans `as` déclenche
  `does not explicitly export attribute` : l'ajouter à l'override
  `[[tool.mypy.overrides]]` de `api/pyproject.toml` avec
  `follow_untyped_imports = true` et `implicit_reexport = true`, plutôt que de
  poser un `# type: ignore`.

Les imports `typing.List`, `Set`, `Dict`, `Optional`, `Union` sont bannis par ruff
(règles TID) : utiliser `list`, `set`, `dict`, `X | None`, `X | Y`.

### Si `front/` est modifié — reproduit le job `build app`

```bash
cd front
npm run format-check             # sinon : npm run format
npm run lint-check               # sinon : npm run lint
npm run test
npm run build                    # lance vue-tsc : les erreurs de types cassent le build
```

### Si une dépendance est mise à jour

Renovate ouvre des MR de mise à jour : une montée de version peut faire apparaître
de nouvelles erreurs `mypy --strict` (types ajoutés en amont) ou de lint. Rejouer
la séquence complète ci-dessus avant de merger.
