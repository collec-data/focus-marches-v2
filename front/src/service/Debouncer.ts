// from https://dev.to/jacobandrewsky/implementing-debouncing-in-vue-22jb

import type { Ref, WatchSource } from 'vue';
import { watch } from 'vue';

/** Délai au-delà duquel une saisie n'est plus considérée comme en cours. */
export const delaiDebounce = 300;

/**
 * Retarde l'appel de `fn` : seule la dernière invocation avant l'expiration du délai est exécutée.
 * Le délai appartient à l'appelant, qui décide si son usage mérite d'être différé.
 */
export function debounce<ARGS extends unknown[]>(fn: (...args: ARGS) => void, delai: number = delaiDebounce): (...args: ARGS) => void {
    let timer: ReturnType<typeof setTimeout> | undefined;
    return (...args: ARGS) => {
        if (timer) {
            clearTimeout(timer);
        }
        timer = setTimeout(() => {
            fn(...args);
        }, delai);
    };
}

/**
 * Envoie la saisie vers `cible` avec du retard, et signale le changement à `surEcriture`.
 *
 * L'appelant choisit les trois : quoi différer, où l'écrire, et ce que ce changement implique —
 * typiquement revenir à la première page. La table qui reçoit la valeur n'a rien à dire du rythme
 * d'une saisie.
 */
export function useEcritureDebouncee(source: WatchSource<string>, cible: Ref<string>, surEcriture?: () => void, delai: number = delaiDebounce): void {
    const ecrire = debounce((valeur: string) => {
        cible.value = valeur;
        surEcriture?.();
    }, delai);

    watch(source, (valeur) => ecrire(valeur));
}
