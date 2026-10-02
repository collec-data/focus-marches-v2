import type { ApiSideDataTable } from '../../src/service/DataTableHelper';
import { useApiSideDataTable } from '../../src/service/DataTableHelper';
import type { FiltresDe, RequeteListe } from '../../src/service/RequeteListe';
import { listAcheteurs, listVendeurs } from '../../src/client';
import { render, waitFor } from '@testing-library/vue';
import type { DataTablePageEvent, DataTableSortEvent } from 'primevue';
import { http, HttpResponse } from 'msw';
import { describe, expect, it } from 'vitest';
import { defineComponent, h, nextTick, ref } from 'vue';
import type { WatchSource } from 'vue';

import { structure } from '../api_test_data';
import { server } from '../setup';

const base = 'http://localhost:3000/';

/** Montre le hook dans un composant, afin que le watcher de la requête soit rattaché au cycle de vie. */
function monter<REQUETE extends RequeteListe>(requete: REQUETE, filtres?: WatchSource<FiltresDe<REQUETE> | undefined>) {
    let table!: ApiSideDataTable<REQUETE>;

    const Composant = defineComponent({
        setup() {
            table = useApiSideDataTable(requete, filtres);
            return () => h('div');
        }
    });

    const { unmount } = render(Composant);
    return { table, unmount };
}

function attendreSucces(table: ApiSideDataTable<RequeteListe>) {
    return waitFor(() => expect(table.etat.value.statut).toBe('succes'));
}

/** Relit les paramètres de chaque appel reçu par l'API, dans l'ordre. */
function capterAppels(url: string, reponse: () => { items: (typeof structure)[]; total: number }) {
    const appels: Record<string, string>[] = [];
    server.use(
        http.get(base + url, ({ request }) => {
            appels.push(Object.fromEntries(new URL(request.url).searchParams));
            return HttpResponse.json(reponse());
        })
    );
    return appels;
}

function attendreAppels(appels: Record<string, string>[], nombre: number) {
    return waitFor(() => expect(appels).toHaveLength(nombre));
}

const page = (valeur: number) => ({ page: valeur }) as DataTablePageEvent;
const tri = (champ: string, ordre: number) => ({ sortField: champ, sortOrder: ordre }) as DataTableSortEvent;

describe('useApiSideDataTable', () => {
    it("déclenche la requête sans que l'appelant ait à valider quoi que ce soit", async () => {
        const appels = capterAppels('structure/acheteur', () => ({ items: [structure], total: 1 }));
        const { table, unmount } = monter(listAcheteurs);

        await attendreSucces(table);

        expect(appels).toHaveLength(1);
        unmount();
    });

    it('rend les lignes et le total de la page servie', async () => {
        const { table, unmount } = monter(listAcheteurs);

        await attendreSucces(table);

        expect(table.items.value).toEqual([structure]);
        expect(table.totalRecords.value).toBe(1);
        unmount();
    });

    it('compose la requête avec la pagination, le tri et le terme de recherche', async () => {
        const appels = capterAppels('structure/acheteur', () => ({ items: [structure], total: 1 }));
        const { table, unmount } = monter(listAcheteurs);
        await attendreSucces(table);

        table.rows.value = 25;
        table.page.value = 2;
        table.sortField.value = 'montant';
        table.sortOrder.value = -1;
        table.filtre.value = 'SOMME';
        await attendreAppels(appels, 2);

        expect(appels[1]).toMatchObject({ limit: '25', offset: '50', ordre: '-1', champs_ordre: 'montant', filtre: 'SOMME' });
        unmount();
    });

    it('relance la requête quand la page ou le tri change', async () => {
        const appels = capterAppels('structure/acheteur', () => ({ items: [structure], total: 1 }));
        const { table, unmount } = monter(listAcheteurs);
        await attendreSucces(table);

        table.onPageChange(page(3));
        table.onSort(tri('nb_contrats', 1));
        await attendreAppels(appels, 2);

        expect(appels[1]).toMatchObject({ offset: '30', champs_ordre: 'nb_contrats', ordre: '1' });
        unmount();
    });

    it("retient la requête tant que l'appelant ne résout pas ses filtres", async () => {
        const appels = capterAppels('structure/acheteur', () => ({ items: [structure], total: 1 }));
        const vendeur = ref<number | undefined>(undefined);
        const { table, unmount } = monter(listAcheteurs, () => (vendeur.value === undefined ? undefined : { vendeur_uid: vendeur.value }));

        await new Promise((resoudre) => setTimeout(resoudre, 20));

        expect(appels).toHaveLength(0);
        expect(table.etat.value.statut).toBe('attente');
        expect(table.items.value).toEqual([]);

        vendeur.value = 42;
        await attendreSucces(table);

        expect(appels).toHaveLength(1);
        expect(appels[0]).toMatchObject({ vendeur_uid: '42' });
        unmount();
    });

    it('envoie les filtres valorisés, et seulement ceux-là', async () => {
        const appels = capterAppels('structure/acheteur', () => ({ items: [structure], total: 1 }));
        const { table, unmount } = monter(listAcheteurs, () => ({ date_fin: new Date('2025-12-31') }));
        await attendreSucces(table);

        expect(appels[0]).toMatchObject({ date_fin: '2025-12-31T00:00:00.000Z', limit: '10' });
        // Un filtre absent ne part pas : le serveur applique alors sa valeur par défaut.
        expect(appels[0]).not.toHaveProperty('date_debut');
        unmount();
    });

    it('passe par chargement sans purger les lignes déjà affichées', async () => {
        capterAppels('structure/acheteur', () => ({ items: [structure], total: 1 }));
        const { table, unmount } = monter(listAcheteurs);
        await attendreSucces(table);

        table.page.value = 1;
        await nextTick();

        expect(table.etat.value.statut).toBe('chargement');
        expect(table.loading.value).toBe(true);
        // La page précédente reste affichée pendant le chargement de la page suivante.
        expect(table.items.value).toEqual([structure]);

        await attendreSucces(table);
        unmount();
    });

    it('refetch rejoue la requête courante', async () => {
        const appels = capterAppels('structure/acheteur', () => ({ items: [structure], total: 1 }));
        const { table, unmount } = monter(listAcheteurs);
        await attendreSucces(table);

        table.refetch();
        await attendreAppels(appels, 2);

        unmount();
    });

    it("refetch ne part pas tant que l'appelant retient ses filtres", async () => {
        const appels = capterAppels('structure/acheteur', () => ({ items: [structure], total: 1 }));
        const { table, unmount } = monter(listAcheteurs, () => undefined);
        await new Promise((resoudre) => setTimeout(resoudre, 20));

        table.refetch();
        await new Promise((resoudre) => setTimeout(resoudre, 20));

        expect(appels).toHaveLength(0);
        expect(table.etat.value.statut).toBe('attente');
        unmount();
    });

    it('sert aussi bien la liste des acheteurs que celle des fournisseurs', async () => {
        const { table, unmount } = monter(listVendeurs, () => ({ acheteur_uid: 7 }));

        await attendreSucces(table);

        expect(table.items.value).toEqual([structure]);
        unmount();
    });
});
