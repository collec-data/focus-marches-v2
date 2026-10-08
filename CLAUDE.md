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
uv run pytest                         # les tests utilisent testcontainers => Docker requis
uv run ruff check                     # sinon : uv run ruff check --fix
uv run ty check                       # AUCUNE erreur tolérée, le job échoue sinon
```

Points d'attention `ty check` :

- toute annotation générique doit être paramétrée : `dict[str, Any]`, jamais `dict` nu ;
- toute fonction doit être annotée (paramètres **et** retour) ;

Les imports `typing.List`, `Set`, `Dict`, `Optional`, `Union` sont bannis par ruff
(règles TID) : utiliser `list`, `set`, `dict`, `X | None`, `X | Y`.

### Si `front/` est modifié — reproduit le job `build app`

```bash
cd front
pnpm run lint-check               # sinon : pnpm run lint
pnpm run test
pnpm run build                    # lance vue-tsc : les erreurs de types cassent le build
```

### Si une dépendance est mise à jour

Renovate ouvre des MR de mise à jour : une montée de version peut faire apparaître
de nouvelles erreurs de typage (types ajoutés en amont) ou de lint. Rejouer
la séquence complète ci-dessus avant de merger.
