<script setup lang="ts">
import type { StructureEtendueDto } from '@/client';
import { getStructure } from '@/client';
import ListeConcessions from '@/components/ListeConcessions.vue';
import { getNow, structureName } from '@/service/HelpersService';
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const acheteurUid = ref(route.params.uid as string);

const acheteur = ref<Partial<StructureEtendueDto>>({});

const dateMin = computed(() => {
    return route.query.dateMin ? new Date(route.query.dateMin as string) : new Date(settings.date_min);
});
const dateMax = computed(() => {
    return route.query.dateMax ? new Date(route.query.dateMax as string) : getNow();
});

function fetchData() {
    getStructure({ path: { uid: parseInt(acheteurUid.value) } }).then((response) => {
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
        <IndicateursCles :acheteurUid :dateMin :dateMax />
        <CategoriePrincipaleDAchat :acheteurUid :dateMin :dateMax />
        <Top12 type="fournisseurs" :acheteurUid :dateMin :dateMax />
        <DistributionTemporelleMarches :acheteurUid :dateMin :dateMax />
        <ListeMarches :nomStructure="structureName(acheteur)" :acheteurUid :dateMin :dateMax />
        <NatureContrats :acheteurUid :dateMin :dateMax />
        <CCAG :acheteurUid :dateMin :dateMax />
        <Procedure :acheteurUid :dateMin :dateMax />
        <ListeConcessions :autoriteConcedanteUid="acheteurUid" :dateMin :dateMax />
    </main>
</template>
