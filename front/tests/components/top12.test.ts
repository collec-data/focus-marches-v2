import { fireEvent, render, screen } from '@testing-library/vue';
import { http, HttpResponse } from 'msw';
import { axe, toHaveNoViolations } from 'jest-axe';
import { expect, it } from 'vitest';
import { structure } from '../api_test_data';
import { server } from '../setup';
import Top12 from '../../src/components/dashboard/Top12.vue';

expect.extend(toHaveNoViolations);

it('top12 acheteurs has no accessibility violation', async () => {
    const { container, unmount } = render(Top12, { propsData: { type: 'acheteurs', dateMin: new Date('2020-01-01'), dateMax: new Date('2026-01-01') } });
    const results = await axe(container);
    expect(results).toHaveNoViolations();
    unmount();
});

it('top12 vendeurs has no accessibility violation', async () => {
    const { container, unmount } = render(Top12, { propsData: { type: 'vendeurs', dateMin: new Date('2020-01-01'), dateMax: new Date('2026-01-01') } });
    const results = await axe(container);
    expect(results).toHaveNoViolations();
    unmount();
});

it('top12 affiche le classement dès que la requête « tous les marchés » a réussi', async () => {
    const { unmount } = render(Top12, { propsData: { type: 'acheteurs', dateMin: new Date('2020-01-01'), dateMax: new Date('2026-01-01') } });
    expect((await screen.findAllByText('Une structure')).length).toBeGreaterThan(0);
    expect(screen.getByRole('tab', { name: 'Tous les marchés' })).toBeTruthy();
    unmount();
});

it("top12 signale l'échec d'un onglet sans masquer les autres", async () => {
    server.use(
        http.get('http://localhost:3000/structure/acheteur', ({ request }) => {
            if (new URL(request.url).searchParams.get('categorie') === 'Services') {
                return HttpResponse.json({}, { status: 500 });
            }
            return HttpResponse.json({ items: [structure], total: 1 });
        })
    );
    const { unmount } = render(Top12, { propsData: { type: 'acheteurs', dateMin: new Date('2020-01-01'), dateMax: new Date('2026-01-01') } });
    expect((await screen.findAllByText('Une structure')).length).toBeGreaterThan(0);

    await fireEvent.click(screen.getByRole('tab', { name: 'Services' }));
    expect(await screen.findByText('Le chargement du classement a échoué')).toBeTruthy();
    unmount();
});

it("top12 affiche un indicateur de chargement tant que la requête de l'onglet est en cours", async () => {
    server.use(
        http.get('http://localhost:3000/structure/acheteur', async ({ request }) => {
            if (new URL(request.url).searchParams.get('categorie') === 'Travaux') {
                await new Promise((resolve) => setTimeout(resolve, 300));
            }
            return HttpResponse.json({ items: [structure], total: 1 });
        })
    );
    const { unmount } = render(Top12, { propsData: { type: 'acheteurs', dateMin: new Date('2020-01-01'), dateMax: new Date('2026-01-01') } });
    await screen.findAllByText('Une structure');

    await fireEvent.click(screen.getByRole('tab', { name: 'Travaux' }));
    expect((await screen.findAllByLabelText('Chargement du classement')).length).toBeGreaterThan(0);
    unmount();
});
