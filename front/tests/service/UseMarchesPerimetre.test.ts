import { render, waitFor } from '@testing-library/vue';
import { http, HttpResponse } from 'msw';
import { describe, expect, it } from 'vitest';
import { defineComponent, h, ref } from 'vue';

import { useMarchesPerimetre } from '../../src/service/UseMarchesPerimetre';
import type { MarchesPerimetre, PerimetreMarches } from '../../src/service/UseMarchesPerimetre';
import { marche } from '../api_test_data';
import { server } from '../setup';

const base = 'http://localhost:3000/';

function monter(perimetre: () => PerimetreMarches | undefined) {
    const capture: { marches?: MarchesPerimetre } = {};
    const Composant = defineComponent({
        setup() {
            capture.marches = useMarchesPerimetre(perimetre);
            return () => h('div');
        }
    });
    const { unmount } = render(Composant);
    return { marches: capture.marches as MarchesPerimetre, unmount };
}

function compter() {
    const requetes: URLSearchParams[] = [];
    server.use(
        http.get(base + 'marche/', ({ request }) => {
            requetes.push(new URL(request.url).searchParams);
            return HttpResponse.json([marche], { headers: { 'X-Resultats-Tronques': 'false', 'X-Limite': '5000' } });
        })
    );
    return requetes;
}

describe('useMarchesPerimetre', () => {
    it('envoie une seule requête pour le périmètre demandé', async () => {
        const requetes = compter();

        const { marches, unmount } = monter(() => ({ acheteurUid: 42, vendeurUid: 7, dateMin: new Date('2020-01-01'), dateMax: new Date('2026-01-01') }));

        await waitFor(() => expect(marches.etat.statut).toBe('succes'));
        expect(requetes).toHaveLength(1);
        expect(requetes[0].get('acheteur_uid')).toBe('42');
        expect(requetes[0].get('vendeur_uid')).toBe('7');
        expect(requetes[0].get('date_debut')).toBeTruthy();
        expect(requetes[0].get('date_fin')).toBeTruthy();
        expect(marches.etat.data).toHaveLength(1);
        unmount();
    });

    it('ne demande rien tant que le périmètre est retenu', async () => {
        const requetes = compter();
        const perimetre = ref<PerimetreMarches | undefined>(undefined);

        const { marches, unmount } = monter(() => perimetre.value);

        expect(marches.etat.statut).toBe('attente');
        expect(requetes).toHaveLength(0);

        perimetre.value = { acheteurUid: 42 };
        await waitFor(() => expect(marches.etat.statut).toBe('succes'));
        expect(requetes).toHaveLength(1);
        unmount();
    });

    it("identifie l'acheteur par son SIRET avant de demander ses marchés", async () => {
        const requetes = compter();
        server.use(http.get(base + 'structure/SIRET/12345678900010', () => HttpResponse.json({ uid: 42 })));

        const { marches, unmount } = monter(() => ({ acheteurSiret: '12345678900010' }));

        expect(marches.etat.statut).toBe('attente');
        await waitFor(() => expect(marches.etat.statut).toBe('succes'));
        expect(requetes).toHaveLength(1);
        expect(requetes[0].get('acheteur_uid')).toBe('42');
        unmount();
    });

    it("expose l'échec d'identification et ne demande aucun marché", async () => {
        const requetes = compter();
        server.use(http.get(base + 'structure/SIRET/00000000000000', () => new HttpResponse(null, { status: 404 })));

        const { marches, unmount } = monter(() => ({ acheteurSiret: '00000000000000' }));

        await waitFor(() => expect(marches.erreurIdentite).not.toBeNull());
        expect(marches.erreurIdentite?.nature).toBe('donnees');
        expect(requetes).toHaveLength(0);
        unmount();
    });

    it('ajoute les paramètres de recherche libres à la requête', async () => {
        const requetes = compter();

        const { marches, unmount } = monter(() => ({ query: { objet: 'ordinateur', montant_min: 100 } }));

        await waitFor(() => expect(marches.etat.statut).toBe('succes'));
        expect(requetes[0].get('objet')).toBe('ordinateur');
        expect(requetes[0].get('montant_min')).toBe('100');
        unmount();
    });

    it('relance la requête quand le périmètre change', async () => {
        const requetes = compter();
        const uid = ref(42);

        const { marches, unmount } = monter(() => ({ acheteurUid: uid.value }));
        await waitFor(() => expect(marches.etat.statut).toBe('succes'));

        uid.value = 43;
        await waitFor(() => expect(requetes).toHaveLength(2));
        expect(requetes[1].get('acheteur_uid')).toBe('43');
        unmount();
    });
});
