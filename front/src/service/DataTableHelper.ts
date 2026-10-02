import type { Options } from '@/client';
import type { RequestResult, TDataShape } from '@/client/client/types.gen';
import { useReactiveFetch } from '@/utils/query';
import { computed, ref, toValue, watch } from 'vue';

import type { DataTablePageEvent, DataTableSortEvent } from 'primevue';

import { debounce } from './Debouncer';

/** Réponse paginée minimale attendue d'une liste dont les données vivent côté serveur. */
interface DonneesListe<ITEM> {
    items: ITEM[];
    total: number;
}

/**
 * Le client généré type ses paramètres via un générique que TypeScript ne résout pas à l'appel : aucune
 * inférence n'en découle, et on ne peut donc récupérer de lui que le type de ses données.
 */
type RequeteListe<ITEM> = (options: never) => RequestResult<DonneesListe<ITEM>, unknown, false, 'fields'>;

/**
 * Pilote une DataTable dont les données vivent côté serveur.
 *
 * La source de la requête est dérivée de la pagination, du tri et de la recherche : les changer relance
 * l'appel, il n'y a donc plus d'état de données dupliqué à resynchroniser à la main. Les valeurs remontées
 * sont calculées sur l'état de la requête, ce qui fait que `loading`, les lignes et le nombre de pages ne
 * peuvent pas être incohérents entre eux.
 *
 * `filtresBase` fournit les paramètres de filtre fixes, et renvoie `undefined` pour retenir la requête :
 * tant que les filtres ne sont pas validés, la liste affichée est celle d'un contexte précédent, pas d'un
 * contexte en invention.
 */
export function useApiSideDataTable<ITEM>(requete: RequeteListe<ITEM>, filtresBase?: () => Record<string, unknown> | undefined) {
    const rows = ref(10); // aka items per page
    const page = ref(0);
    const sortField = ref('nom');
    const sortOrder = ref(1);
    const search = ref('');
    /** Ce que la requête utilise réellement, décalé pour ne pas partir à chaque frappe. */
    const filtre = ref('');

    const first = computed(() => page.value * rows.value);

    const source = computed<Options<TDataShape, false> | undefined>(() => {
        const base = filtresBase?.();
        if (!base) {
            return undefined;
        }
        return {
            query: {
                ...base,
                limit: rows.value,
                offset: first.value,
                ordre: sortOrder.value,
                // Les champs de tri sont décrits par endpoint dans le client généré ; la table les reçoit
                // comme des chaînes et la requête les transmet au serveur.
                champs_ordre: sortField.value,
                filtre: filtre.value
            }
        } as unknown as Options<TDataShape, false>;
    });

    const lister = (options: Options<TDataShape, false>) => requete({ query: toValue(options)?.query } as never);

    // Pagination et tri ne changent pas le contexte des données : on garde les lignes affichées pendant la
    // requête, sinon la table se vide à chaque changement de page.
    const { etat, refetch } = useReactiveFetch(lister, source, { conserverDonnees: () => true });

    const onFilter = debounce(() => {
        page.value = 0;
        filtre.value = search.value.toUpperCase();
    });

    watch(search, () => onFilter());

    function onSort(event: DataTableSortEvent) {
        sortField.value = event.sortField as string;
        sortOrder.value = event.sortOrder as number;
    }

    function onPageChange(event: DataTablePageEvent) {
        page.value = event.page;
    }

    return {
        search,
        /** Termes réellement envoyés : c'est ce que voit l'export, pas la saisie en cours. */
        filtre,
        page,
        first,
        totalRecords: computed(() => etat.value.data?.total ?? 0),
        loading: computed(() => etat.value.statut === 'chargement'),
        etat,
        items: computed(() => etat.value.data?.items ?? []),
        rows,
        sortOrder,
        sortField,
        onSort,
        onFilter,
        onPageChange,
        refetch
    };
}

export const rowsPerPageOptions = [10, 25, 50];
