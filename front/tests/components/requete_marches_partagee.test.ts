import { render, screen, waitFor } from '@testing-library/vue';
import { http, HttpResponse } from 'msw';
import { describe, expect, it } from 'vitest';

import { marche } from '../api_test_data';
import { mockRouter } from '../mocks';
import { server } from '../setup';
import Acheteur from '../../src/views/Acheteur.vue';
import Fournisseur from '../../src/views/Fournisseur.vue';

const base = 'http://localhost:3000/';

function compterRequetesMarches() {
    const requetes: URLSearchParams[] = [];
    server.use(
        http.get(base + 'marche/', ({ request }) => {
            requetes.push(new URL(request.url).searchParams);
            return HttpResponse.json([marche]);
        })
    );
    return requetes;
}

describe('requête des marchés partagée entre le tableau et le graphique', () => {
    it("ne part qu'une fois sur la fiche acheteur", async () => {
        await mockRouter({ uid: '42' });
        const requetes = compterRequetesMarches();

        const { unmount } = render(Acheteur);

        await waitFor(() => expect(screen.getByText('Lorem ipsum dolor')).toBeTruthy());
        await screen.findByRole('heading', { name: 'Distribution temporelle des marchés' });
        expect(requetes).toHaveLength(1);
        expect(requetes[0].get('acheteur_uid')).toBe('42');
        unmount();
    });

    it("ne part qu'une fois sur la fiche fournisseur", async () => {
        await mockRouter({ uid: '42' });
        const requetes = compterRequetesMarches();

        const { unmount } = render(Fournisseur);

        await waitFor(() => expect(screen.getByText('Lorem ipsum dolor')).toBeTruthy());
        await screen.findByRole('heading', { name: 'Distribution temporelle des marchés' });
        expect(requetes).toHaveLength(1);
        expect(requetes[0].get('vendeur_uid')).toBe('42');
        unmount();
    });
});
