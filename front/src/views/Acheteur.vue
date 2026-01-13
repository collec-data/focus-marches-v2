<script setup lang="ts">
import type { StructureEtendueDto } from '@/client';
import { getStructure } from '@/client';
import CarteAcheteursFournisseurs from '@/components/dashboard/CarteAcheteursFournisseurs.vue';
import ListeConcessions from '@/components/ListeConcessions.vue';
import { getNow, structureName } from '@/service/HelpersService';
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const acheteurUid = ref(parseInt(route.params.uid as string));
const acheteurSiret = computed(() => acheteur?.value.identifiant);
const acheteur = ref<Partial<StructureEtendueDto>>({});

const dateMin = computed(() => {
    return route.query.dateMin ? new Date(route.query.dateMin as string) : new Date(settings.date_min);
});
const dateMax = computed(() => {
    return route.query.dateMax ? new Date(route.query.dateMax as string) : getNow();
});

function fetchData() {
    getStructure({ path: { uid: acheteurUid.value } }).then((response) => {
        if (response.data) {
            acheteur.value = response.data;
        }
    });
}

watch(acheteurUid, () => {
    fetchData();
});

onMounted(() => {
    fetchData();
});
</script>

<template>
    <main className="card">
        <h1>Tableau de bord de l'acheteur : {{ structureName(acheteur) }}</h1>
        <p>Cette page vous présente les données essentielles du profil d'acheteur de {{ structureName(acheteur) }} , enrichies avec des données complémentaires.</p>
        <DetailsAcheteur :acheteur />
        <FiltreDates :dateMin :dateMax />
        <IndicateursCles :acheteurUid :acheteurSiret :dateMin :dateMax />
        <CategoriePrincipaleDAchat :acheteurUid :acheteurSiret :dateMin :dateMax />
        <Top12 type="fournisseurs" :acheteurUid :dateMin :dateMax />
        <CarteAcheteursFournisseurs :acheteur :dateMin :dateMax />
        <DistributionTemporelleMarches :acheteurUid :acheteurSiret :dateMin :dateMax />
        <ListeMarches :nomStructure="structureName(acheteur)" :acheteurUid :acheteurSiret :dateMin :dateMax />
        <NatureContrats :acheteurUid :acheteurSiret :dateMin :dateMax />
        <CCAG :acheteurUid :acheteurSiret :dateMin :dateMax />
        <Procedure :acheteurUid :dateMin :dateMax />
        <AchatDurable :acheteurUid :dateMin :dateMax />
        <ListeConcessions :autoriteConcedanteUid="'' + acheteurUid" :dateMin :dateMax />
    </main>
</template>
