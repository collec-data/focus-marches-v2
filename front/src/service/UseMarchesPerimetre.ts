import { getListeMarches } from '@/client';
import type { GetListeMarchesData, MarcheAllegeDto } from '@/client';
import { useStructureIdentifiee } from '@/service/UseStructureIdentifiee';
import type { ErreurReactiveFetch, ResultatReactiveFetch } from '@/utils/query';
import { useReactiveFetch } from '@/utils/query';
import { computed } from 'vue';

export type QueryMarches = NonNullable<GetListeMarchesData['query']>;

/**
 * Les marchés à demander. Les structures sont désignées par leur uid, ou à défaut par le SIRET de l'acheteur,
 * qui est alors identifié avant toute requête. `query` complète ou remplace les filtres déduits du reste.
 */
export type PerimetreMarches = {
    acheteurUid?: number | null;
    acheteurSiret?: string | null;
    vendeurUid?: number | null;
    dateMin?: Date | null;
    dateMax?: Date | null;
    query?: QueryMarches;
};

/** Les marchés d'un périmètre, que plusieurs sections d'une même page affichent sans les redemander. */
export type MarchesPerimetre = {
    readonly etat: ResultatReactiveFetch<MarcheAllegeDto[]>;
    /** Échec de l'identification de l'acheteur par son SIRET, ou `null`. Dans ce cas, aucun marché n'est demandé. */
    readonly erreurIdentite: ErreurReactiveFetch | null;
    refetch: () => void;
    refetchIdentite: () => void;
};

/**
 * Demande une seule fois les marchés d'un périmètre, pour tous les composants qui les affichent.
 *
 * Tant que `perimetre` renvoie `undefined`, rien n'est demandé : l'état reste `attente`. Il en va de même tant
 * que l'acheteur désigné par son SIRET n'est pas identifié.
 */
export function useMarchesPerimetre(perimetre: () => PerimetreMarches | undefined): MarchesPerimetre {
    const {
        uid,
        erreur: erreurIdentite,
        refetch: refetchIdentite
    } = useStructureIdentifiee(
        () => perimetre()?.acheteurUid,
        () => perimetre()?.acheteurSiret
    );

    const options = computed(() => {
        const demande = perimetre();
        if (demande === undefined || uid.value === undefined) {
            return undefined;
        }
        return {
            query: {
                date_debut: demande.dateMin ?? undefined,
                date_fin: demande.dateMax ?? undefined,
                acheteur_uid: uid.value ?? undefined,
                vendeur_uid: demande.vendeurUid ?? undefined,
                ...demande.query
            }
        };
    });

    const { etat, refetch } = useReactiveFetch(getListeMarches, options);

    return {
        get etat() {
            return etat.value;
        },
        get erreurIdentite() {
            return erreurIdentite.value;
        },
        refetch,
        refetchIdentite
    };
}
