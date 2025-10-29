<script setup lang="ts">
import type { IndicateursDto } from '@/client';
import { getIndicateursMarcheIndicateursGet } from '@/client';
import { formatCurrency } from '@/service/HelpersService';
import { onMounted, ref, watch } from 'vue';
const props = defineProps({
    acheteurUid: { type: [String, null], default: null },
    vendeurUid: { type: [String, null], default: null },
    dateMin: { type: [Date, null], default: null },
    dateMax: { type: [Date, null], default: null },
    query: {
        type: Object,
        default: () => {
            return {};
        }
    }
});

const indicateurs = ref({} as IndicateursDto);

function fetchData() {
    getIndicateursMarcheIndicateursGet({
        query: {
            date_debut: props.dateMin,
            date_fin: props.dateMax,
            acheteur_uid: props.acheteurUid,
            vendeur_uid: props.vendeurUid,
            ...props.query
        }
    }).then((data) => {
        if (data.data) {
            indicateurs.value = data.data;
        }
    });
}

watch([() => props.dateMin, () => props.dateMax, () => props.acheteurUid, () => props.vendeurUid, () => props.query], () => {
    fetchData();
});

onMounted(() => {
    fetchData();
});
</script>

<template>
    <section class="flex flex-col">
        <div>
            <h2 class="title">Indicateurs clés</h2>
            <p class="subtitle">
                Principaux indicateurs des <span class="highlight">{{ indicateurs.periode }} derniers mois</span>.
            </p>
        </div>
        <div class="flex flex-row flex-wrap gap-10 mt-10">
            <div class="indicateur">
                <i class="pi pi-calendar"></i>
                <div class="label">PÉRIODE</div>
                <div class="value">{{ indicateurs.periode }} mois</div>
            </div>
            <div class="indicateur">
                <i class="pi pi-receipt"></i>
                <div class="label">NB DE CONTRATS</div>
                <div class="value">{{ indicateurs.nb_contrats }}</div>
            </div>
            <div class="indicateur">
                <i class="pi pi-calculator"></i>
                <div class="label">MONTANT TOTAL</div>
                <div class="value">{{ indicateurs.montant_total ? formatCurrency(parseFloat(indicateurs.montant_total)) : '' }}</div>
            </div>
            <div v-if="acheteurUid == null" class="indicateur">
                <i class="pi pi-users"></i>
                <div class="label">NB ACHETEURS</div>
                <div class="value">{{ indicateurs.nb_acheteurs }}</div>
            </div>
            <div v-if="vendeurUid == null" class="indicateur">
                <i class="pi pi-users"></i>
                <div class="label">NB FOURNISSEURS</div>
                <div class="value">{{ indicateurs.nb_fournisseurs }}</div>
            </div>
            <div class="indicateur">
                <i class="pi pi-sitemap"></i>
                <div class="label">NB CONTRATS AVEC SOUS TRAITANCE</div>
                <div class="value">{{ indicateurs.nb_sous_traitance }}</div>
            </div>
            <div class="indicateur">
                <i class="pi pi-star"></i>
                <div class="label">NB CONTRATS AVEC DES CONSIDERATIONS ENVIRONNEMENTALES ET SOCIALES</div>
                <div class="value"></div>
            </div>
            <div class="indicateur">
                <i class="pi pi-globe"></i>
                <div class="label">NB CONTRATS AVEC DES CONSIDERATIONS ENVIRONNEMENTALES</div>
                <div class="value"></div>
            </div>
            <div class="indicateur">
                <i class="pi pi-eye"></i>
                <div class="label">NB CONTRATS AVEC DES CONSIDERATIONS SOCIALES</div>
                <div class="value"></div>
            </div>
            <div class="indicateur">
                <i class="pi pi-lightbulb"></i>
                <div class="label">NB CONTRATS INNOVANTS</div>
                <div class="value">{{ indicateurs.nb_innovant }}</div>
            </div>
        </div>
        <BoutonIframe v-if="acheteurUid" :acheteurUid path="indicateurs" name="Des indicateurs sur les marchés publics passés" />
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
    font-weight: 900;
}

.pi {
    color: var(--p-primary-color);
    font-size: 4rem;
}
</style>
