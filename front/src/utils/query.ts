import type { Options } from '@/client';
import type { RequestResult, TDataShape } from '@/client/client/types.gen';
import type { ShallowRef, WatchSource } from 'vue';
import { onWatcherCleanup, ref, shallowRef, toValue, watch } from 'vue';

/**
 * Nature d'un échec, décidée par le statut HTTP et non par l'appelant :
 * - `technique` : la requête peut réussir en étant rejouée (panne, 5xx) ;
 * - `donnees`   : la requête ne peut pas réussir en étant rejouée (référence inconnue, paramètres invalides).
 */
export type NatureErreur = 'technique' | 'donnees';

export type ErreurReactiveFetch = {
    nature: NatureErreur;
    /** Statut HTTP, ou `null` si la requête n'a pas atteint l'API. */
    statut: number | null;
    /** Charge utile brute de l'API. Destinée au diagnostic, jamais affichée. */
    detail: unknown;
};

type ResultatAttente = {
    statut: 'attente';
    data: null;
    erreur: null;
};

type ResultatChargement<DATA> = {
    statut: 'chargement';
    /**
     * Données de la requête précédente, conservées lorsque `conserverDonnees` est actif.
     * `null` sur un premier chargement, ou lorsque la requête change de contexte.
     */
    data: DATA | null;
    erreur: null;
};

type ResultatSucces<DATA> = {
    statut: 'succes';
    data: DATA;
    erreur: null;
};

type ResultatErreur = {
    statut: 'erreur';
    data: null;
    erreur: ErreurReactiveFetch;
};

export type ResultatReactiveFetch<DATA> = ResultatAttente | ResultatChargement<DATA> | ResultatSucces<DATA> | ResultatErreur;

export type ConfigReactiveFetch = {
    /**
     * Conserve les données précédentes pendant un rechargement. À n'activer que pour la pagination et le tri,
     * qui ne changent pas le contexte des données. Un changement de contexte (filtre, période, structure)
     * doit au contraire purger : les données précédentes y sont fausses.
     */
    conserverDonnees?: WatchSource<boolean>;
};

/** Résultat d'un `useReactiveFetch`, avec la fonction de rejeu manuel. */
export type ReactiveFetch<DATA> = {
    etat: ShallowRef<ResultatReactiveFetch<DATA>>;
    /** Rejoue la requête avec les options courantes. Sans effet si la requête n'a pas encore pu partir. */
    refetch: () => void;
};

function classer(statut: number | null): NatureErreur {
    return statut !== null && statut < 500 ? 'donnees' : 'technique';
}

/** Signature commune à toutes les fonctions du SDK, en mode non throwant et en style `fields`. */
type RequeteSdk<O> = (options: O) => RequestResult<unknown, unknown, false, 'fields'>;

/** Type de la charge utile d'une requête, déduit de la fonction SDK plutôt que d'un paramètre générique. */
type DonneesDe<F extends RequeteSdk<never>> = NonNullable<Awaited<ReturnType<F>>['data']>;

/**
 * Déclenche une requête SDK réactive, et expose son état.
 *
 * La source d'options vaut `undefined` tant qu'une dépendance n'est pas résolue : aucune requête ne part,
 * et l'état reste `attente`. La résolution de la dépendance est donc un `computed` côté appelant, ce qui
 * laisse TypeScript restreindre le type des options au seul moment où la requête part.
 *
 * Une requête annulée — par une nouvelle requête ou par le démontage du composant — n'est pas un échec :
 * elle ne produit aucun état, le `watch` qui l'a annulée ayant déjà pris le relais.
 */
export function useReactiveFetch<F extends RequeteSdk<O>, O extends Options<TDataShape, false>>(fetchFunc: F, optionsSource: WatchSource<O | undefined>, config: ConfigReactiveFetch = {}): ReactiveFetch<DonneesDe<F>> {
    type DATA = DonneesDe<F>;

    const etat = shallowRef<ResultatReactiveFetch<DATA>>({ statut: 'attente', data: null, erreur: null });
    const rejeux = ref(0);
    let controleur: AbortController | null = null;

    watch(
        [optionsSource, rejeux],
        ([options]) => {
            controleur?.abort();

            if (options === undefined) {
                etat.value = { statut: 'attente', data: null, erreur: null };
                return;
            }

            const courant = new AbortController();
            controleur = courant;
            const { signal } = courant;

            etat.value = {
                statut: 'chargement',
                data: toValue(config.conserverDonnees) ? etat.value.data : null,
                erreur: null
            };

            // La surcharge de `fetch` passe par une variable : l'ajout d'une propriété à un objet littéral
            // passé en argument serait sinon refusé comme propriété en trop.
            const requete = { ...options, fetch: (input: RequestInfo | URL, init?: RequestInit) => fetch(input, { ...init, signal }) };

            fetchFunc(requete).then(
                (resultat) => {
                    if (signal.aborted) {
                        return;
                    }
                    if (resultat.error !== undefined) {
                        // Le type généré annonce une `Response`, mais le SDK renvoie `undefined` quand `fetch`
                        // lui-même échoue : seule une réponse HTTP permet de qualifier la nature de l'échec.
                        const statut = resultat.response?.status ?? null;
                        etat.value = { statut: 'erreur', data: null, erreur: { nature: classer(statut), statut, detail: resultat.error } };
                        return;
                    }
                    etat.value = { statut: 'succes', data: resultat.data as DATA, erreur: null };
                },
                (raison) => {
                    if (signal.aborted) {
                        return;
                    }
                    etat.value = { statut: 'erreur', data: null, erreur: { nature: 'technique', statut: null, detail: raison } };
                }
            );

            onWatcherCleanup(() => {
                courant.abort();
            });
        },
        { immediate: true }
    );

    return {
        etat,
        refetch: () => {
            rejeux.value += 1;
        }
    };
}
