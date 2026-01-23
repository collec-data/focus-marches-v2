<script setup lang="ts">
import { getIndicateurs } from '@/client';
import { getAcheteurUid } from '@/service/GetAcheteurService';
import { formatCurrency, formatNumber } from '@/service/HelpersService';
import { onMounted, ref, watch } from 'vue';

import type { IndicateursDto } from '@/client';

const props = defineProps({
    acheteurUid: { type: [Number, null], default: null },
    acheteurSiret: { type: [String, null], default: null },
    vendeurUid: { type: [Number, null], default: null },
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

async function fetchData() {
    const acheteurUid = await getAcheteurUid(props.acheteurUid, props.acheteurSiret);
    if (acheteurUid || props.vendeurUid || props.query) {
        getIndicateurs({
            query: {
                date_debut: props.dateMin,
                date_fin: props.dateMax,
                acheteur_uid: acheteurUid,
                vendeur_uid: props.vendeurUid,
                ...props.query
            }
        }).then((data) => {
            if (data.data) {
                indicateurs.value = data.data;
            }
        });
    }
}

watch([() => props.dateMin, () => props.dateMax, () => props.acheteurUid, () => props.vendeurUid, () => props.query], () => {
    fetchData();
});

onMounted(() => {
    fetchData();
});

function removeNnbsp(text: string): string {
    return text.replaceAll(String.fromCharCode(8239), ' ');
}
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
                <div class="value">{{ removeNnbsp(formatNumber(indicateurs.nb_contrats).toString()) }}</div>
            </div>
            <div class="indicateur">
                <i class="pi pi-calculator"></i>
                <div class="label">MONTANT TOTAL</div>
                <div class="value">{{ removeNnbsp(indicateurs.montant_total ? formatCurrency(parseFloat(indicateurs.montant_total)) : '') }}</div>
            </div>
            <div v-if="acheteurUid == null" class="indicateur">
                <i class="pi pi-users"></i>
                <div class="label">NB ACHETEURS</div>
                <div class="value">{{ removeNnbsp(formatNumber(indicateurs.nb_acheteurs).toString()) }}</div>
            </div>
            <div v-if="vendeurUid == null" class="indicateur">
                <i class="pi pi-users"></i>
                <div class="label">NB FOURNISSEURS</div>
                <div class="value">{{ removeNnbsp(formatNumber(indicateurs.nb_fournisseurs).toString()) }}</div>
            </div>
            <div class="indicateur">
                <i class="pi pi-sitemap"></i>
                <div class="label">NB CONTRATS AVEC SOUS TRAITANCE</div>
                <div class="value">{{ removeNnbsp(formatNumber(indicateurs.nb_sous_traitance).toString()) }}</div>
            </div>
            <div class="indicateur">
                <i class="pi pi-star"></i>
                <div class="label">NB CONTRATS AVEC DES CONSIDERATIONS ENVIRONNEMENTALES ET SOCIALES</div>
                <div class="value">{{ removeNnbsp(formatNumber(indicateurs.nb_considerations_sociale_env).toString()) }}</div>
            </div>
            <div class="indicateur">
                <i class="pi pi-globe"></i>
                <div class="label">NB CONTRATS AVEC DES CONSIDERATIONS ENVIRONNEMENTALES</div>
                <div class="value">{{ removeNnbsp(formatNumber(indicateurs.nb_considerations_env).toString()) }}</div>
            </div>
            <div class="indicateur">
                <i class="pi pi-eye"></i>
                <div class="label">NB CONTRATS AVEC DES CONSIDERATIONS SOCIALES</div>
                <div class="value">{{ removeNnbsp(formatNumber(indicateurs.nb_considerations_sociales).toString()) }}</div>
            </div>
            <div class="indicateur">
                <i class="pi pi-lightbulb"></i>
                <div class="label">NB CONTRATS INNOVANTS</div>
                <div class="value">{{ removeNnbsp(formatNumber(indicateurs.nb_innovant).toString()) }}</div>
            </div>
        </div>
        <BoutonIframe v-if="props.acheteurSiret" :acheteurSiret="props.acheteurSiret" path="indicateurs" name="Des indicateurs sur les marchés publics passés" />
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
