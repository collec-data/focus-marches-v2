import { render } from '@testing-library/vue';
import { axe, toHaveNoViolations } from 'jest-axe';
import { expect, it, vi } from 'vitest';
import ErreursImportations from '../src/views/ErreursImportations.vue';
import Recherche from '../src/views/Recherche.vue';

expect.extend(toHaveNoViolations);

vi.mock('vue-router');
async function mockRouter(): Promise<void> {
    const VueRouter = await import('vue-router');
    VueRouter.useRoute.mockReturnValue({ path: '/', query: {}, params: {} });
}

it('other views has no accessibility violations', async () => {
    const views = [Recherche, ErreursImportations];
    for (const view of views) {
        await mockRouter(); // attendu, même vide, par la page d'erreurs d'importation

        const { container, unmount } = render(view);
        const results = await axe(container);
        expect(results).toHaveNoViolations();

        unmount();
        // ne pas oublier de démonter chaque composant testé,
        // au risque d'avoir des erreurs de multiple élément main
    }
});
