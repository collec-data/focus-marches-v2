import { render, screen, waitFor } from '@testing-library/vue';
import { http, HttpResponse } from 'msw';
import { describe, expect, it } from 'vitest';

import { ModaliteExecution, TechniqueAchat } from '../../src/client';
import ListeMarches from '../../src/components/ListeMarches.vue';
import ModaleMarche from '../../src/components/ModaleMarche.vue';
import { marche } from '../api_test_data';
import { mockRouter } from '../mocks';
import { server } from '../setup';

const base = 'http://localhost:3000/';
const avertissement = 'Le nombre de résultats affichés est limité aux 5000 plus récents. Veuillez affiner vos filtres.';
const tronque = { headers: { 'X-Resultats-Tronques': 'true', 'X-Limite': '5000' } };
const complet = { headers: { 'X-Resultats-Tronques': 'false', 'X-Limite': '5000' } };

describe('ListeMarches', () => {
    it('avertit quand la limite de résultats est atteinte', async () => {
        await mockRouter({ uid: 42 });
        server.use(http.get(base + 'marche/', () => HttpResponse.json([marche], tronque)));

        const { unmount } = render(ListeMarches, { props: { acheteurUid: 42 } });

        await waitFor(() => expect(screen.getByText(avertissement)).toBeTruthy());
        unmount();
    });

    it("n'avertit pas quand la limite n'est pas atteinte", async () => {
        await mockRouter({ uid: 42 });
        server.use(http.get(base + 'marche/', () => HttpResponse.json([marche], complet)));

        const { unmount } = render(ListeMarches, { props: { acheteurUid: 42 } });

        await waitFor(() => expect(screen.getByText('Lorem ipsum dolor')).toBeTruthy());
        expect(screen.queryByText(/limité aux/)).toBeNull();
        unmount();
    });
});

describe('ModaleMarche', () => {
    const accordCadre = { ...marche, techniques_achat: [TechniqueAchat.ACCORD_CADRE], modalites_execution: [ModaliteExecution.MARCHÉS_SUBSÉQUENTS], modifications: [] };

    it('avertit quand la liste des marchés subséquents est tronquée', async () => {
        server.use(
            http.get(base + 'marche/1234', () => HttpResponse.json(accordCadre)),
            http.get(base + 'marche/', () => HttpResponse.json([marche], tronque))
        );

        const { unmount } = render(ModaleMarche, { props: { modelValue: 1234 } });

        await waitFor(() => expect(screen.getByText(avertissement)).toBeTruthy());
        unmount();
    });

    it("n'avertit pas quand la liste des marchés subséquents est complète", async () => {
        server.use(
            http.get(base + 'marche/1234', () => HttpResponse.json(accordCadre)),
            http.get(base + 'marche/', () => HttpResponse.json([marche], complet))
        );

        const { unmount } = render(ModaleMarche, { props: { modelValue: 1234 } });

        await waitFor(() => expect(screen.getAllByText('Lorem ipsum dolor').length).toBeGreaterThan(0));
        expect(screen.queryByText(/limité aux/)).toBeNull();
        unmount();
    });
});
