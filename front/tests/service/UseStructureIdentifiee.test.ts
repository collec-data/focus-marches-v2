import type { ResultatResolutionIdentite } from '../../src/service/UseStructureIdentifiee';
import { useStructureIdentifiee } from '../../src/service/UseStructureIdentifiee';
import { render, waitFor } from '@testing-library/vue';
import { http, HttpResponse } from 'msw';
import { describe, expect, it } from 'vitest';
import { defineComponent, h, ref } from 'vue';

import { server } from '../setup';

const base = 'http://localhost:3000/';

function monter(acheteurUid: () => number | null | undefined, acheteurSiret: () => string | null | undefined, config?: { structure?: boolean }) {
    let resolution!: ResultatResolutionIdentite;

    const Composant = defineComponent({
        setup() {
            resolution = useStructureIdentifiee(acheteurUid, acheteurSiret, config);
            return () => h('div');
        }
    });

    const { unmount } = render(Composant);
    return { ...resolution, unmount };
}

function structure(siret: string, uid: number) {
    return server.use(http.get(base + 'structure/SIRET/' + siret, () => HttpResponse.json({ uid })));
}

describe('useStructureIdentifiee', () => {
    it("n'interroge pas l'API quand l'uid est déjà résolu plus haut", async () => {
        let appels = 0;
        server.use(
            http.get(base + 'structure/SIRET/:siret', () => {
                appels += 1;
                return HttpResponse.json({ uid: 1 });
            })
        );

        const { uid, unmount } = monter(
            () => 42,
            () => '12345678901234'
        );

        await waitFor(() => expect(uid.value).toBe(42));
        await new Promise((resoudre) => setTimeout(resoudre, 20));

        expect(appels).toBe(0);
        unmount();
    });

    it('ne demande aucun acheteur quand ni uid ni SIRET ne sont fournis', async () => {
        let appels = 0;
        server.use(
            http.get(base + 'structure/SIRET/:siret', () => {
                appels += 1;
                return HttpResponse.json({ uid: 1 });
            })
        );

        const { uid, erreur, unmount } = monter(
            () => undefined,
            () => null
        );

        await waitFor(() => expect(uid.value).toBeNull());
        await new Promise((resoudre) => setTimeout(resoudre, 20));

        expect(appels).toBe(0);
        expect(erreur.value).toBeNull();
        unmount();
    });

    it('résout le uid depuis le SIRET, et une seule fois', async () => {
        let appels = 0;
        server.use(
            http.get(base + 'structure/SIRET/:siret', () => {
                appels += 1;
                return HttpResponse.json({ uid: 77 });
            })
        );

        const { uid, unmount } = monter(
            () => undefined,
            () => '12345678901234'
        );

        // Tant que la structure n'est pas identifiée, l'appelant ne doit rien lancer.
        expect(uid.value).toBeUndefined();

        await waitFor(() => expect(uid.value).toBe(77));
        await new Promise((resoudre) => setTimeout(resoudre, 20));

        expect(appels).toBe(1);
        unmount();
    });

    it('laisse uid indéfini quand la résolution échoue, pour interdire toute requête dépendante', async () => {
        server.use(http.get(base + 'structure/SIRET/:siret', () => HttpResponse.json({ detail: 'Structure inconnue' }, { status: 404 })));

        const { uid, erreur, unmount } = monter(
            () => undefined,
            () => '99999999999999'
        );

        await waitFor(() => expect(erreur.value).not.toBeNull());

        // Un uid indéfini est ce qui empêche une requête sans filtre : les marchés de la plateforme
        // entière ne doivent jamais être présentés comme ceux de la structure demandée.
        expect(uid.value).toBeUndefined();
        expect(erreur.value).toMatchObject({ nature: 'donnees', statut: 404 });
        unmount();
    });

    it('rejoue la résolution après une panne technique', async () => {
        let appels = 0;
        server.use(
            http.get(base + 'structure/SIRET/:siret', () => {
                appels += 1;
                return appels === 1 ? new HttpResponse(null, { status: 503 }) : HttpResponse.json({ uid: 77 });
            })
        );

        const { uid, erreur, refetch, unmount } = monter(
            () => undefined,
            () => '12345678901234'
        );

        await waitFor(() => expect(erreur.value).toMatchObject({ nature: 'technique', statut: 503 }));

        refetch();
        await waitFor(() => expect(uid.value).toBe(77));
        expect(appels).toBe(2);
        unmount();
    });

    it('redémarre la résolution quand le SIRET change', async () => {
        structure('11111111111111', 1);
        structure('22222222222222', 2);

        const siret = ref<string | null>('11111111111111');
        const { uid, unmount } = monter(
            () => undefined,
            () => siret.value
        );

        await waitFor(() => expect(uid.value).toBe(1));

        siret.value = '22222222222222';
        await waitFor(() => expect(uid.value).toBe(2));
        unmount();
    });

    it("ne charge pas la fiche quand l'uid est déjà connu, sauf demande explicite", async () => {
        let appels = 0;
        server.use(
            http.get(base + 'structure/:uid', () => {
                appels += 1;
                return HttpResponse.json({ uid: 42, identifiant: '12345678901234' });
            })
        );

        const sansFiche = monter(
            () => 42,
            () => null
        );
        await waitFor(() => expect(sansFiche.uid.value).toBe(42));
        await new Promise((resoudre) => setTimeout(resoudre, 20));
        expect(appels).toBe(0);
        expect(sansFiche.structure.value).toBeNull();
        sansFiche.unmount();

        const avecFiche = monter(
            () => 42,
            () => null,
            { structure: true }
        );
        await waitFor(() => expect(avecFiche.structure.value).not.toBeNull());
        expect(appels).toBe(1);
        avecFiche.unmount();
    });

    it('expose la fiche résolue depuis le SIRET', async () => {
        server.use(http.get(base + 'structure/SIRET/:siret', () => HttpResponse.json({ uid: 77, identifiant: '12345678901234' })));

        const {
            uid,
            structure: fiche,
            unmount
        } = monter(
            () => undefined,
            () => '12345678901234',
            { structure: true }
        );

        await waitFor(() => expect(fiche.value).toMatchObject({ uid: 77 }));
        expect(uid.value).toBe(77);
        unmount();
    });
});
