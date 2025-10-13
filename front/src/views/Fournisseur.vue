<script setup lang="ts">
import { ref, watch } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const vendeurUid = route.params.uid as string;

const dates = ref({
    min: route.query?.dateMin ? new Date(route.query.dateMin as string) : null,
    max: route.query?.dateMax ? new Date(route.query.dateMax as string) : null
});

watch([() => vendeurUid, () => route.query?.dateMin, () => route.query?.dateMax], () => {
    dates.value.max = route.query?.dateMax ? new Date(route.query.dateMax as string) : null;
    dates.value.min = route.query?.dateMin ? new Date(route.query.dateMin as string) : null;
});
</script>

<template>
    <main className="card">
        <h1>Tableau de bord du fournisseur :</h1>
        <p>Cette page vous présente les données essentielles des profils d'acheteurs ayant attribué des contrats au fournisseur "", enrichies avec des données complémentaires.</p>

        <h2>Localisation et contexte</h2>

        <FiltreDates :dateMin="dates.min" :dateMax="dates.max" />
        <IndicateursCles :vendeurUid :dateMin="dates.min" :dateMax="dates.max" />
        <ListeMarches :vendeurUid :dateMin="dates.min" :dateMax="dates.max" />
        <NatureContrats :vendeurUid :dateMin="dates.min" :dateMax="dates.max" />
        <Procedure :vendeurUid :dateMin="dates.min" :dateMax="dates.max" />
    </main>
</template>
