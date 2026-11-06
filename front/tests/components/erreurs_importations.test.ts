import { render, waitFor } from '@testing-library/vue';
import { http, HttpResponse } from 'msw';
import { expect, it } from 'vitest';

import ErreursImportations from '../../src/views/ErreursImportations.vue';

import { server } from '../setup';

it('envoie le jour choisi dans le sélecteur, sans le décaler', async () => {
    const VueRouter = await import('vue-router');
    // Minuit en heure locale, comme le renvoie le sélecteur de date.
    const debut = new Date(2026, 10, 7);
    const fin = new Date(2026, 10, 9);
    VueRouter.useRoute.mockReturnValue({ params: {}, path: '/erreurs', query: { dateMin: debut.toISOString(), dateMax: fin.toISOString() } });

    let filtres = new URLSearchParams();
    server.use(
        http.get('http://localhost:3000/erreurs-import/stats', ({ request }) => {
            filtres = new URL(request.url).searchParams;
            return HttpResponse.json([]);
        })
    );

    const { unmount } = render(ErreursImportations);

    await waitFor(() => expect(filtres.get('date_debut')).not.toBeNull());
    expect(filtres.get('date_debut')).toBe('2026-11-07T00:00:00.000Z');
    expect(filtres.get('date_fin')).toBe('2026-11-09T00:00:00.000Z');
    unmount();
});
