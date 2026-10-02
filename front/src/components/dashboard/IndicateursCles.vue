<script setup lang="ts">
import { getIndicateurs } from '@/client';
import { formatCurrency, formatNumber } from '@/service/HelpersService';
import { useStructureIdentifiee } from '@/service/UseStructureIdentifiee';
import { useReactiveFetch } from '@/utils/query';
import { computed } from 'vue';

import type { PropType } from 'vue';

const props = defineProps({
    acheteurUid: { type: Number as PropType<number | null>, required: false },
    acheteurSiret: { type: String as PropType<string | null>, required: false },
    vendeurUid: { type: Number as PropType<number | null>, required: false },
    dateMin: { type: Date as PropType<Date | null>, required: false },
    dateMax: { type: Date as PropType<Date | null>, required: false },
    query: { type: Object as PropType<Record<string, unknown>>, default: () => ({}) }
});

const {
    uid,
    erreur: erreurAcheteur,
    refetch: refetchAcheteur
} = useStructureIdentifiee(
    () => props.acheteurUid,
    () => props.acheteurSiret
);

const options = computed(() => {
    if (uid.value === undefined) {
        return undefined;
    }
    return {
        query: {
            date_debut: props.dateMin ?? undefined,
            date_fin: props.dateMax ?? undefined,
            acheteur_uid: uid.value ?? undefined,
            vendeur_uid: props.vendeurUid ?? undefined,
            ...props.query
        }
    };
});

const { etat, refetch } = useReactiveFetch(getIndicateurs, options);

// `succes` est le seul état où les indicateurs sont des mesures. Ailleurs, il n'y a rien à afficher.
const indicateurs = computed(() => (etat.value.statut === 'succes' ? etat.value.data : null));
const chargement = computed(() => etat.value.statut === 'chargement');

function removeNnbsp(text: string): string {
    return text.replaceAll(String.fromCharCode(8239), ' ');
}
</script>

<template>
    <section class="flex flex-col">
        <div>
            <h2 class="title">Indicateurs clés</h2>
            <p v-if="indicateurs" class="subtitle">
                Principaux indicateurs des <span class="highlight">{{ indicateurs.periode }} derniers mois</span>.
            </p>
        </div>

        <ErreurChargement v-if="erreurAcheteur" :erreur="erreurAcheteur" message="Aucune structure ne correspond à ce SIRET" @retry="refetchAcheteur" />
        <ErreurChargement v-else-if="etat.statut === 'erreur'" :erreur="etat.erreur" message="Le chargement des indicateurs a échoué" @retry="refetch" />
        <div v-else-if="chargement || etat.statut === 'succes'" class="flex flex-row flex-wrap gap-10 mt-10">
            <div class="indicateur">
                <i class="pi pi-calendar"></i>
                <div class="label">PÉRIODE</div>
                <Skeleton v-if="chargement" width="4rem" height="1.25rem" class="mx-auto" />
                <template v-else>
                    <div class="value">{{ indicateurs!.periode === null ? 'Période absente' : indicateurs!.periode + 'mois' }}</div>
                </template>
            </div>
            <div class="indicateur">
                <i class="pi pi-receipt"></i>
                <div class="label">NB DE CONTRATS</div>
                <Skeleton v-if="chargement" width="4rem" height="1.25rem" class="mx-auto" />
                <div v-else class="value">{{ removeNnbsp(formatNumber(indicateurs!.nb_contrats)) }}</div>
            </div>
            <div class="indicateur">
                <i class="pi pi-calculator"></i>
                <div class="label">MONTANT TOTAL</div>
                <Skeleton v-if="chargement" width="4rem" height="1.25rem" class="mx-auto" />
                <div v-else class="value">{{ removeNnbsp(formatCurrency(parseFloat(indicateurs!.montant_total))) }}</div>
            </div>
            <div v-if="uid === null" class="indicateur">
                <i class="pi pi-users"></i>
                <div class="label">NB ACHETEURS</div>
                <Skeleton v-if="chargement" width="4rem" height="1.25rem" class="mx-auto" />
                <div v-else class="value">{{ removeNnbsp(formatNumber(indicateurs!.nb_acheteurs)) }}</div>
            </div>
            <div v-if="vendeurUid == null" class="indicateur">
                <i class="pi pi-users"></i>
                <div class="label">NB FOURNISSEURS</div>
                <Skeleton v-if="chargement" width="4rem" height="1.25rem" class="mx-auto" />
                <div v-else class="value">{{ removeNnbsp(formatNumber(indicateurs!.nb_fournisseurs)) }}</div>
            </div>
            <div class="indicateur">
                <i class="pi pi-sitemap"></i>
                <div class="label">NB CONTRATS AVEC SOUS TRAITANCE</div>
                <Skeleton v-if="chargement" width="4rem" height="1.25rem" class="mx-auto" />
                <div v-else class="value">{{ removeNnbsp(formatNumber(indicateurs!.nb_sous_traitance)) }}</div>
            </div>
            <div class="indicateur">
                <i class="pi pi-star"></i>
                <div class="label">NB CONTRATS AVEC DES CONSIDERATIONS ENVIRONNEMENTALES ET SOCIALES</div>
                <Skeleton v-if="chargement" width="4rem" height="1.25rem" class="mx-auto" />
                <div v-else class="value">{{ removeNnbsp(formatNumber(indicateurs!.nb_considerations_sociale_env)) }}</div>
            </div>
            <div class="indicateur">
                <i class="pi pi-globe"></i>
                <div class="label">NB CONTRATS AVEC DES CONSIDERATIONS ENVIRONNEMENTALES</div>
                <Skeleton v-if="chargement" width="4rem" height="1.25rem" class="mx-auto" />
                <div v-else class="value">{{ removeNnbsp(formatNumber(indicateurs!.nb_considerations_env)) }}</div>
            </div>
            <div class="indicateur">
                <i class="pi pi-eye"></i>
                <div class="label">NB CONTRATS AVEC DES CONSIDERATIONS SOCIALES</div>
                <Skeleton v-if="chargement" width="4rem" height="1.25rem" class="mx-auto" />
                <div v-else class="value">{{ removeNnbsp(formatNumber(indicateurs!.nb_considerations_sociales)) }}</div>
            </div>
            <div class="indicateur">
                <i class="pi pi-lightbulb"></i>
                <div class="label">NB CONTRATS INNOVANTS</div>
                <Skeleton v-if="chargement" width="4rem" height="1.25rem" class="mx-auto" />
                <div v-else class="value">{{ removeNnbsp(formatNumber(indicateurs!.nb_innovant)) }}</div>
            </div>
        </div>
        <BoutonIframe v-if="acheteurSiret" :path="'acheteur/' + acheteurSiret + '/indicateurs'" name="Des indicateurs sur les marchés publics passés" />
    </section>
</template>

<style scoped>
.indicateur {
    flex-basis: 15rem;
    flex-shrink: 0;
    text-align: center;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.value {
    font-size: large;
    word-spacing: 0.3rem;
}

.pi {
    color: var(--p-primary-color);
    font-size: 4rem;
}
</style>
