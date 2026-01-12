import { render } from '@testing-library/vue';
import { axe, toHaveNoViolations } from 'jest-axe';
import { expect, it, vi } from 'vitest';
import ErreursImportations from '../src/views/ErreursImportations.vue';
import Recherche from '../src/views/Recherche.vue';

expect.extend(toHaveNoViolations);
// ne pas oublier de démonter chaque composant testé,
// au risque d'avoir des erreurs de multiple élément main

vi.mock('vue-router');
async function mockRouter(params): Promise<void> {
    const VueRouter = await import('vue-router');
    VueRouter.useRoute.mockReturnValue({
        params: params,
        path: '/',
        query: {}
    });
}

it('other views has no accessibility violations', async () => {
    const views = [
        { view: Recherche, config: {} },
        { view: ErreursImportations, config: {} }
    ];
    for (let i = 0; i < views.length; ++i) {
        await mockRouter({}); // attendu, même vide, par la page d'erreurs d'importation
        const { container, unmount } = render(views[i].view, views[i].config);
        const results = await axe(container);
        expect(results).toHaveNoViolations();
        unmount();
    }
});
