# FRONT END

## Briques techniques

Ce projet utilise :

- le framework [VueJS](https://vuejs.org/) en [Typescript](https://www.typescriptlang.org/) avec [Vite](https://vite.dev/)
- la bibliothèque de composants [PrimeVue](https://primevue.org/) et le framework CSS [Tailwind CSS](https://tailwindcss.com/), sur une base de template [Sakai](https://sakai.primevue.org/)
- le framework de test [Vitest](https://vitest.dev/)

## Initialisation pour le développement

- Avoir installé NodeJS (voir [.tool-versions](.tool-versions) pour la version requise)
- Installer les dépendances `npm install`

## Tâches courantes

Depuis le dossier courant (`/front`) :

- Lancer le serveur de dév avec `npm run dev``
- Régénérer le client pour s'adapter aux changements de l'API avec `npm run gen`
- Executer en local la CI gitlab avec `npm ci && npm run format-check && npm run lint-check && npm run test`

## Tests ![coverage](<https://gitlab.csm.ovh/focus-marches/focusmarchev2/badges/main/coverage.svg?job=build app>)

Les tests sont situés dans le dossier [tests](./tests/). Il s'agit pour l'instant de tests au niveau des vues (ce qui inclus donc tous les composants qui y sont appelés) ou des services.

Les tests font appel au framework [Vitest](https://vitest.dev/) et peuvent être exécutés avec la commande `npm run test` ou directement depuis VSCode. La couverture de code est calculée et indique les lignes non couvertes fichier par fichier.

## Accessibilité

L'accessibilité est surveillée à plusieurs niveaux, en se basant principalement sur les outils avec le moteur [Axe](https://www.deque.com/axe/).

Manuellement dans le navigateur : il est conseillé d'installer et d'exécuter régulièrement l'extension Axe DevTools (présente sur [Firefox](https://addons.mozilla.org/en-US/firefox/addon/axe-devtools/) & [Chrome](https://chromewebstore.google.com/detail/axe-devtools-web-accessib/lhdoppojpmngadmnindnejefpokejbdd)).

Automatiquement dans la CI :

- eslint exécute le plugin [`vuejs-accessibility`](https://vue-a11y.github.io/eslint-plugin-vuejs-accessibility/)
- des tests d'accessibilité sont présents dans [la suite de test](./tests/accessibility.test.ts) en se basant sur le paquet [jest-axe](https://github.com/nickcolley/jest-axe#readme)

NB : Ces tests automatiques sont le strict minimum pour s'assurer d'une accessibilité correcte de l'application, mais ils ne sont pas exhaustifs pour autant et **ne garantissent pas que l'application soit entièrement accessible**. Ils doivent être complétés par d'autres outils, des tests avec des lecteurs d'écran ou encore des sessions avec des utilisateurs concernés.
