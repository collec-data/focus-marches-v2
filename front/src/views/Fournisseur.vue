<script setup lang="ts">
import type { StructureEtendueDto } from '@/client';
import { getStructureStructureUidGet } from '@/client';
import { onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const vendeurUid = route.params.uid as string;

const dates = ref({
    min: route.query?.dateMin ? new Date(route.query.dateMin as string) : null,
    max: route.query?.dateMax ? new Date(route.query.dateMax as string) : null
});

const vendeur = ref<Partial<StructureEtendueDto>>({});

function fetchData() {
    getStructureStructureUidGet({ path: { uid: parseInt(vendeurUid) } }).then((response) => {
        if (response.data) {
            vendeur.value = response.data;
        }
    });
}

watch([() => vendeurUid, () => route.query?.dateMin, () => route.query?.dateMax], () => {
    dates.value.max = route.query?.dateMax ? new Date(route.query.dateMax as string) : null;
    dates.value.min = route.query?.dateMin ? new Date(route.query.dateMin as string) : null;
    fetchData();
});

onMounted(() => {
    fetchData();
});
</script>

<template>
    <main className="card">
        <h1>Tableau de bord du fournisseur : {{ vendeur.nom }}</h1>
        <p>Cette page vous présente les données essentielles des profils d'acheteurs ayant attribué des contrats au fournisseur {{ vendeur.nom }}, enrichies avec des données complémentaires.</p>
        <DetailsFournisseur :vendeur />
        <FiltreDates :dateMin="dates.min" :dateMax="dates.max" />
        <IndicateursCles :vendeurUid :dateMin="dates.min" :dateMax="dates.max" />
        <DistributionTemporelleMarches :vendeurUid :dateMin="dates.min" :dateMax="dates.max" />
        <ListeMarches :vendeurUid :dateMin="dates.min" :dateMax="dates.max" />
        <NatureContrats :vendeurUid :dateMin="dates.min" :dateMax="dates.max" />
        <Procedure :vendeurUid :dateMin="dates.min" :dateMax="dates.max" />
    </main>
</template>
