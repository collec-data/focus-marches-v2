<script setup lang="ts">
import type { StructureEtendueDto } from '@/client';
import { getStructureStructureUidGet } from '@/client';
import { onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const acheteurUid = route.params.uid as string;

const acheteur = ref<Partial<StructureEtendueDto>>({});

function fetchData() {
    getStructureStructureUidGet({ path: { uid: parseInt(acheteurUid) } }).then((response) => {
        if (response.data) {
            acheteur.value = response.data;
        }
    });
}

watch([() => acheteurUid, () => route.query?.dateMin, () => route.query?.dateMax], () => {
    dates.value.max = route.query?.dateMax ? new Date(route.query.dateMax as string) : null;
    dates.value.min = route.query?.dateMin ? new Date(route.query.dateMin as string) : null;

    fetchData();
});

onMounted(() => {
    fetchData();
});

const dates = ref({
    min: route.query?.dateMin ? new Date(route.query.dateMin as string) : null,
    max: route.query?.dateMax ? new Date(route.query.dateMax as string) : null
});
</script>

<template>
    <main className="card">
        <h1>Tableau de bord de l'acheteur : {{ acheteur.nom }}</h1>
        <p>Cette page vous présente les données essentielles du profil d'acheteur de {{ acheteur.nom }} , enrichies avec des données complémentaires.</p>

        <div>
            <h2>Localisation et contexte</h2>
            <ul>
                <li>Dénomination : {{ acheteur.nom }}</li>
                <li>Date création :</li>
                <li>Sigle : {{ acheteur.sigle }}</li>
                <li>Adresse : {{ acheteur.adresse }}</li>
                <li>Cat entreprise :</li>
                <li>Cat juridique : {{ acheteur.cat_juridique }}</li>
                <li>NAF : {{ acheteur.naf }}</li>
                <li>Effectifs : {{ acheteur.effectifs }} (en {{ acheteur.date_effectifs }})</li>
            </ul>
        </div>
        <FiltreDates :dateMin="dates.min" :dateMax="dates.max" />
        <IndicateursCles :acheteurUid :dateMin="dates.min" :dateMax="dates.max" />
        <ListeMarches :acheteurUid :dateMin="dates.min" :dateMax="dates.max" />
        <NatureContrats :acheteurUid :dateMin="dates.min" :dateMax="dates.max" />
        <CCAG :acheteurUid :dateMin="dates.min" :dateMax="dates.max" />
        <Procedure :acheteurUid :dateMin="dates.min" :dateMax="dates.max" />
    </main>
</template>
