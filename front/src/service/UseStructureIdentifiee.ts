import type { StructureEtendueDto } from '@/client';
import { getStructure, getStructureId } from '@/client';
import type { ErreurReactiveFetch } from '@/utils/query';
import { useReactiveFetch } from '@/utils/query';
import type { MaybeRefOrGetter, Ref } from 'vue';
import { computed, toValue } from 'vue';

export type ResultatResolutionIdentite = {
    /**
     * uid de la structure. Trois valeurs distinctes, à ne jamais confondre :
     * - un nombre : la structure est identifiée ;
     * - `null`    : aucune structure n'est demandée, donc aucun filtre de ce côté ;
     * - `undefined` : la résolution est en cours ou a échoué, et l'appelant ne doit lancer aucune requête.
     */
    uid: Readonly<Ref<number | null | undefined>>;
    /** Structure identifiée, ou `null` tant qu'elle ne l'est pas. Toujours `null` si `structure` n'est pas demandé. */
    structure: Readonly<Ref<StructureEtendueDto | null>>;
    /** Échec de la résolution, ou `null` tant qu'elle n'a pas échoué. */
    erreur: Readonly<Ref<ErreurReactiveFetch | null>>;
    refetch: () => void;
};

/**
 * Résout l'identité d'une structure : l'uid déjà connu, le SIRET sinon.
 *
 * Un SIRET est ce qui déclare l'identité : tant qu'il est présent, la structure doit être identifiée avant
 * tout calcul. En son absence, si aucun uid n'est fourni non plus, aucune structure n'est demandée et rien
 * n'a besoin d'être résolu.
 *
 * Une résolution en échec laisse `uid` à `undefined` et renseigne `erreur`.
 *
 * `structure` inclue la fiche de la structure en plus de son uid. Elle n'est pas demandée par défaut.
 */
export function useStructureIdentifiee(uid: MaybeRefOrGetter<number | null | undefined>, siret: MaybeRefOrGetter<string | null | undefined>, config: { structure?: boolean } = {}): ResultatResolutionIdentite {
    const parUidConnu = computed(() => typeof toValue(uid) === 'number');

    const sourceParUid = computed(() => {
        const valeur = toValue(uid);
        return config.structure && typeof valeur === 'number' ? { path: { uid: valeur } } : undefined;
    });

    const sourceParSiret = computed(() => {
        if (parUidConnu.value) {
            return undefined;
        }
        const identifiant = toValue(siret);
        return identifiant ? { path: { id: identifiant, type_id: 'SIRET' as const } } : undefined;
    });

    const parUid = useReactiveFetch(getStructure, sourceParUid);
    const parSiret = useReactiveFetch(getStructureId, sourceParSiret);

    // Une seule des deux voies est active.
    const etatCourant = computed(() => (parUidConnu.value ? parUid.etat.value : parSiret.etat.value));

    const uidResolu = computed<number | null | undefined>(() => {
        const fourni = toValue(uid);
        if (typeof fourni === 'number') {
            return fourni;
        }
        if (!toValue(siret)) {
            return null;
        }
        return parSiret.etat.value.statut === 'succes' ? parSiret.etat.value.data.uid : undefined;
    });

    const structure = computed<StructureEtendueDto | null>(() => {
        const courant = etatCourant.value;
        return courant.statut === 'succes' ? courant.data : null;
    });

    const erreur = computed(() => {
        const courant = etatCourant.value;
        return courant.statut === 'erreur' ? courant.erreur : null;
    });

    const refetch = () => (parUidConnu.value ? parUid.refetch() : parSiret.refetch());

    return { uid: uidResolu, structure, erreur, refetch };
}
