import type { IndicateursDto } from '../../src/client';
import { getIndicateurs } from '../../src/client';
import type { ConfigReactiveFetch, ResultatReactiveFetch } from '../../src/utils/query';
import { useReactiveFetch } from '../../src/utils/query';
import { render, waitFor } from '@testing-library/vue';
import { http, HttpResponse } from 'msw';
import { describe, expect, it } from 'vitest';
import { defineComponent, h, nextTick, ref, shallowRef, watch } from 'vue';
import type { ShallowRef } from 'vue';

import { server } from '../setup';

const base = 'http://localhost:3000/';

type Etat = ShallowRef<ResultatReactiveFetch<IndicateursDto>>;

/** Montre le hook dans un composant, afin que le watcher soit rattaché au cycle de vie et désabonné au démontage. */
function monter(source: () => { query?: { acheteur_uid?: number } } | undefined, config?: ConfigReactiveFetch) {
    const capture: { etat: Etat; refetch: () => void } = { etat: shallowRef({ statut: 'attente', data: null, erreur: null }), refetch: () => {} };

    const Composant = defineComponent({
        setup() {
            const requete = useReactiveFetch(getIndicateurs, source, config);
            capture.etat = requete.etat;
            capture.refetch = requete.refetch;
            return () => h('div');
        }
    });

    const { unmount } = render(Composant);
    return { etat: capture.etat, refetch: capture.refetch, unmount };
}

function attendre(etat: Etat, statut: ResultatReactiveFetch<IndicateursDto>['statut']) {
    return waitFor(() => expect(etat.value.statut).toBe(statut));
}

describe('useReactiveFetch', () => {
    it('ne part pas tant que les options sont undefined, et attend la dépendance', async () => {
        let appels = 0;
        server.use(
            http.get(base + 'marche/indicateurs', () => {
                appels += 1;
                return HttpResponse.json({ nb_contrats: 7 });
            })
        );

        const uid = ref<number | undefined>(undefined);
        const { etat, unmount } = monter(() => (uid.value === undefined ? undefined : { query: { acheteur_uid: uid.value } }));

        expect(etat.value.statut).toBe('attente');
        expect(etat.value.data).toBeNull();

        uid.value = 42;
        await attendre(etat, 'succes');
        expect(appels).toBe(1);
        expect(etat.value.data).toMatchObject({ nb_contrats: 7 });

        unmount();
    });

    it('passe par chargement avant de rendre les données', async () => {
        const etats: string[] = [];
        const uid = ref<number | undefined>(undefined);
        const source = () => (uid.value === undefined ? undefined : { query: { acheteur_uid: uid.value } });

        const { etat, unmount } = monter(source);
        watch(etat, (valeur) => etats.push(valeur.statut), { immediate: true });

        uid.value = 42;
        await attendre(etat, 'succes');

        expect(etats).toContain('chargement');
        expect(etats.at(-1)).toBe('succes');

        unmount();
    });

    it('ne rend aucune donnée pendant le chargement', async () => {
        server.use(http.get(base + 'marche/indicateurs', () => HttpResponse.json({ nb_contrats: 0 })));

        const { etat, unmount } = monter(() => ({ query: { acheteur_uid: 42 } }));

        // Un compteur à zéro ne doit pas être confondu avec une valeur réelle : avant la réponse, il n'y a rien.
        expect(etat.value.data).toBeNull();

        await attendre(etat, 'succes');
        // Un zéro reçu de l'API est en revanche une donnée réelle.
        expect(etat.value.data).toMatchObject({ nb_contrats: 0 });

        unmount();
    });

    it('classe une erreur de référence en erreur de données, non rejouable', async () => {
        server.use(http.get(base + 'marche/indicateurs', () => HttpResponse.json({ detail: 'Structure inconnue' }, { status: 404 })));

        const { etat, unmount } = monter(() => ({ query: { acheteur_uid: 42 } }));

        await attendre(etat, 'erreur');
        expect(etat.value.erreur).toMatchObject({ nature: 'donnees', statut: 404 });
        expect(etat.value.data).toBeNull();

        unmount();
    });

    it('classe une panne serveur en erreur technique, rejouable', async () => {
        server.use(http.get(base + 'marche/indicateurs', () => new HttpResponse(null, { status: 500 })));

        const { etat, unmount } = monter(() => ({ query: { acheteur_uid: 42 } }));

        await attendre(etat, 'erreur');
        expect(etat.value.erreur).toMatchObject({ nature: 'technique', statut: 500 });

        unmount();
    });

    it('classe une panne réseau en erreur technique sans statut', async () => {
        server.use(http.get(base + 'marche/indicateurs', () => HttpResponse.error()));

        const { etat, unmount } = monter(() => ({ query: { acheteur_uid: 42 } }));

        await attendre(etat, 'erreur');
        expect(etat.value.erreur).toMatchObject({ nature: 'technique', statut: null });

        unmount();
    });

    it('ne transforme pas une requête annulée en erreur', async () => {
        let appels = 0;
        server.use(
            http.get(base + 'marche/indicateurs', async () => {
                appels += 1;
                const numero = appels;
                await new Promise((resoudre) => setTimeout(resoudre, 40));
                return HttpResponse.json({ nb_contrats: numero });
            })
        );

        const etats: string[] = [];
        const uid = ref(1);
        const { etat, unmount } = monter(() => ({ query: { acheteur_uid: uid.value } }));
        watch(etat, (valeur) => etats.push(valeur.statut), { immediate: true });

        // La première requête est en vol et se fait annuler avant de répondre.
        uid.value = 2;
        await attendre(etat, 'succes');

        expect(etats).not.toContain('erreur');
        expect(appels).toBe(2);
        expect(etat.value.data).toMatchObject({ nb_contrats: 2 });

        unmount();
    });

    it("ne produit pas d'erreur au démontage du composant", async () => {
        server.use(
            http.get(base + 'marche/indicateurs', async () => {
                await new Promise((resoudre) => setTimeout(resoudre, 40));
                return HttpResponse.json({ nb_contrats: 3 });
            })
        );

        const etats: string[] = [];
        const { etat, unmount } = monter(() => ({ query: { acheteur_uid: 42 } }));
        watch(etat, (valeur) => etats.push(valeur.statut), { immediate: true });

        unmount();
        await new Promise((resoudre) => setTimeout(resoudre, 80));

        expect(etats).not.toContain('erreur');
    });

    it('refetch rejoue la requête avec les mêmes options', async () => {
        let appels = 0;
        server.use(
            http.get(base + 'marche/indicateurs', () => {
                appels += 1;
                return HttpResponse.json({ nb_contrats: appels });
            })
        );

        const { etat, refetch, unmount } = monter(() => ({ query: { acheteur_uid: 42 } }));
        await attendre(etat, 'succes');
        expect(appels).toBe(1);

        refetch();
        await nextTick();
        expect(etat.value.statut).toBe('chargement');

        await attendre(etat, 'succes');
        expect(appels).toBe(2);

        unmount();
    });

    it('refetch ne part pas tant que la dépendance est non résolue', async () => {
        let appels = 0;
        server.use(
            http.get(base + 'marche/indicateurs', () => {
                appels += 1;
                return HttpResponse.json({ nb_contrats: 1 });
            })
        );

        const uid = ref<number | undefined>(undefined);
        const { etat, refetch, unmount } = monter(() => (uid.value === undefined ? undefined : { query: { acheteur_uid: uid.value } }));

        refetch();
        await new Promise((resoudre) => setTimeout(resoudre, 20));

        expect(appels).toBe(0);
        expect(etat.value.statut).toBe('attente');

        unmount();
    });

    it('purge les données quand la requête change de contexte', async () => {
        server.use(
            http.get(base + 'marche/indicateurs', ({ request }) => {
                const uid = new URL(request.url).searchParams.get('acheteur_uid');
                return HttpResponse.json({ nb_contrats: uid === '1' ? 100 : 200 });
            })
        );

        const uid = ref(1);
        const { etat, unmount } = monter(() => ({ query: { acheteur_uid: uid.value } }));
        await attendre(etat, 'succes');
        expect(etat.value.data).toMatchObject({ nb_contrats: 100 });

        uid.value = 2;
        await nextTick();
        expect(etat.value.statut).toBe('chargement');
        // Les chiffres de l'acheteur précédent seraient faux pour le nouveau.
        expect(etat.value.data).toBeNull();

        await attendre(etat, 'succes');
        unmount();
    });

    it('conserve les données quand conserverDonnees est actif', async () => {
        server.use(
            http.get(base + 'marche/indicateurs', ({ request }) => {
                const uid = new URL(request.url).searchParams.get('acheteur_uid');
                return HttpResponse.json({ nb_contrats: uid === '1' ? 100 : 200 });
            })
        );

        const uid = ref(1);
        const { etat, unmount } = monter(() => ({ query: { acheteur_uid: uid.value } }), { conserverDonnees: () => true });
        await attendre(etat, 'succes');
        expect(etat.value.data).toMatchObject({ nb_contrats: 100 });

        uid.value = 2;
        await nextTick();
        expect(etat.value.statut).toBe('chargement');
        expect(etat.value.data).toMatchObject({ nb_contrats: 100 });

        await attendre(etat, 'succes');
        expect(etat.value.data).toMatchObject({ nb_contrats: 200 });

        unmount();
    });
});
