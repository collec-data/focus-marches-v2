import { render } from '@testing-library/vue';
import { axe, toHaveNoViolations } from 'jest-axe';
import { expect, it, vi } from 'vitest';
import Accueil from '../src/views/Accueil.vue';
import Acheteur from '../src/views/Acheteur.vue';
import Acheteurs from '../src/views/Acheteurs.vue';
import ErreursImportations from '../src/views/ErreursImportations.vue';
import Fournisseur from '../src/views/Fournisseur.vue';
import Fournisseurs from '../src/views/Fournisseurs.vue';
import Recherche from '../src/views/Recherche.vue';

expect.extend(toHaveNoViolations);
// ne pas oublier de démonter chaque composant testé,
// au risque d'avoir des erreurs de multiple élément main

it('other views has no accessibility violations', async () => {
    const views = [
        { view: Recherche, config: {} },
        { view: ErreursImportations, config: {} }
    ];
    for (let i = 0; i < views.length; ++i) {
        const { container, unmount } = render(views[i].view, views[i].config);
        const results = await axe(container);
        expect(results).toHaveNoViolations();
        unmount();
    }
});
