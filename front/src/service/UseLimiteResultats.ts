import { limiteSiTronque } from '@/service/HelpersService';
import type { ResultatReactiveFetch } from '@/utils/query';
import type { ComputedRef, Ref } from 'vue';
import { computed } from 'vue';

/** La limite de résultats de l'API quand la réponse affichée a été tronquée, `null` sinon. À passer à `AvertissementLimite`. */
export function useLimiteResultats(etat: Readonly<Ref<ResultatReactiveFetch<unknown>>>): ComputedRef<number | null> {
    return computed(() => (etat.value.statut === 'succes' ? limiteSiTronque(etat.value.entetes) : null));
}
