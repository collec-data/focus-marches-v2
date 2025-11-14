<script setup lang="ts">
import type { StructureEtendueDto } from '@/client';
import { getStructureStructureUidGet } from '@/client';
import { structureName } from '@/service/HelpersService';
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const vendeurUid = ref(route.params.uid as string);

const vendeur = ref<Partial<StructureEtendueDto>>({});

const dateMin = computed(() => {
    return route.query.dateMin ? new Date(route.query.dateMin as string) : null;
});
const dateMax = computed(() => {
    return route.query.dateMax ? new Date(route.query.dateMax as string) : null;
});

function fetchData() {
    getStructureStructureUidGet({ path: { uid: parseInt(vendeurUid.value) } }).then((response) => {
        if (response.data) {
            vendeur.value = response.data;
        }
    });
}

watch(vendeurUid, () => {
    fetchData();
});

onMounted(() => {
    fetchData();
});
</script>

<template>
    <main className="card">
        <h1>Tableau de bord du fournisseur : {{ structureName(vendeur) }}</h1>
        <p>Cette page vous présente les données essentielles des profils d'acheteurs ayant attribué des contrats au fournisseur {{ structureName(vendeur) }}, enrichies avec des données complémentaires.</p>
        <DetailsFournisseur :vendeur />
        <FiltreDates :dateMin :dateMax />
        <IndicateursCles :vendeurUid :dateMin :dateMax />
        <CategoriePrincipaleDAchat :vendeurUid :dateMin :dateMax />
        <Top12 type="acheteurs" :vendeurUid :dateMin :dateMax />
        <DistributionTemporelleMarches :vendeurUid :dateMin :dateMax />
        <ListeMarches :nomStructure="structureName(vendeur)" :vendeurUid :dateMin :dateMax />
        <NatureContrats :vendeurUid :dateMin :dateMax />
        <Procedure :vendeurUid :dateMin :dateMax />
        <ListeConcessions :concessionnaireUid="vendeurUid" :dateMin :dateMax />
    </main>
</template>
