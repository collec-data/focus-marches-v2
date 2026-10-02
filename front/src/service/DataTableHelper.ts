import type { ChampTriDe, ChargeDe, FiltresDe, ItemDe, PageListe, QueryDe, RequeteListe } from '@/service/RequeteListe';
import type { ResultatReactiveFetch } from '@/utils/query';
import { useReactiveFetch } from '@/utils/query';
import type { ComputedRef, Ref, ShallowRef, WatchSource } from 'vue';
import { computed, ref, toValue } from 'vue';

import type { DataTablePageEvent, DataTableSortEvent } from 'primevue';

/**
 * Une table dont les données vivent côté serveur : ce que la table pilote, ce qu'elle envoie, et ce
 * qu'elle reçoit.
 */
export type ApiSideDataTable<REQUETE extends RequeteListe> = {
    /**
     * Terme de recherche réellement envoyé. La saisie, elle, appartient à l'appelant : c'est lui qui
     * décide à quel rythme elle devient ce terme, et lui qui remet la page à zéro quand il change.
     */
    filtre: Ref<string>;
    page: Ref<number>;
    /** Première ligne affichée, déduite de la page et du nombre de lignes par page. */
    first: ComputedRef<number>;
    rows: Ref<number>;
    sortField: Ref<string>;
    sortOrder: Ref<number>;
    items: ComputedRef<ItemDe<REQUETE>[]>;
    totalRecords: ComputedRef<number>;
    loading: ComputedRef<boolean>;
    etat: ShallowRef<ResultatReactiveFetch<ChargeDe<REQUETE>>>;
    onSort: (event: DataTableSortEvent) => void;
    onPageChange: (event: DataTablePageEvent) => void;
    refetch: () => void;
};

/**
 * Pilote une DataTable dont les données vivent côté serveur.
 *
 * La source de la requête est dérivée de la pagination et du tri : les changer relance l'appel, il
 * n'y a donc plus d'état de données dupliqué à resynchroniser à la main. Les valeurs remontées sont
 * calculées sur l'état de la requête, ce qui fait que `loading`, les lignes et le nombre de pages ne
 * peuvent pas être incohérents entre eux.
 *
 * `filtres` fournit les paramètres propres à l'endpoint, et peut les retenir en renvoyant `undefined` :
 * tant que les filtres ne sont pas validés, la liste affichée reste celle d'un contexte précédent, pas
 * d'un contexte en invention. Ne pas passer de filtres vaut ne pas en filtrer, pas les retenir.
 */
export function useApiSideDataTable<REQUETE extends RequeteListe>(requete: REQUETE, filtres?: WatchSource<FiltresDe<REQUETE> | undefined>): ApiSideDataTable<REQUETE> {
    const rows = ref(10); // aka items per page
    const page = ref(0);
    const sortField = ref('nom');
    const sortOrder = ref(1);
    const filtre = ref('');

    const first = computed(() => page.value * rows.value);

    const lister = (options: { query: QueryDe<REQUETE> }) => requete(options);

    // La source est un getter plutôt qu'un `computed` : `useReactiveFetch` y déduit le type des
    // options, et il doit y retrouver les paramètres que l'endpoint déclare.
    const source = (): { query: QueryDe<REQUETE> } | undefined => {
        const base: FiltresDe<REQUETE> | undefined = filtres === undefined ? {} : toValue(filtres);
        if (base === undefined) {
            return undefined;
        }
        return {
            query: {
                ...base,
                limit: rows.value,
                offset: first.value,
                ordre: sortOrder.value,
                filtre: filtre.value,
                // Les champs de tri sont décrits par endpoint dans le client généré ; la table les reçoit
                // comme des chaînes et la requête les transmet au serveur.
                champs_ordre: sortField.value as ChampTriDe<REQUETE>
            }
        };
    };

    // Pagination et tri ne changent pas le contexte des données : on garde les lignes affichées pendant la
    // requête, sinon la table se vide à chaque changement de page.
    const { etat, refetch } = useReactiveFetch(lister, source, { conserverDonnees: () => true });

    function onSort(event: DataTableSortEvent) {
        sortField.value = event.sortField as string;
        sortOrder.value = event.sortOrder as number;
    }

    function onPageChange(event: DataTablePageEvent) {
        page.value = event.page;
    }

    /**
     * La page servie par l'endpoint. Sa forme n'est résolvable qu'à l'appel, une fois `REQUETE`
     * résolue : le compilateur ne voit pas à travers la requête, générique par nature. La page vient
     * bien de l'endpoint, que la contrainte de `RequeteListe` a déjà vérifié.
     */
    const charge = computed(() => etat.value.data as PageListe<ItemDe<REQUETE>> | null);

    return {
        filtre,
        page,
        first,
        rows,
        sortField,
        sortOrder,
        onSort,
        onPageChange,
        refetch,
        items: computed(() => charge.value?.items ?? []),
        totalRecords: computed(() => charge.value?.total ?? 0),
        loading: computed(() => etat.value.statut === 'chargement'),
        etat
    };
}

export const rowsPerPageOptions = [10, 25, 50];
