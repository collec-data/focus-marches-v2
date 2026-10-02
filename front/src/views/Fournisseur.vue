<script setup lang="ts">
import { getStructure } from '@/client';
import { getNow, structureName } from '@/service/HelpersService';
import { useReactiveFetch } from '@/utils/query';
import { computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();

const vendeurUid = computed(() => {
    const uid = Number.parseInt(String(route.params.uid ?? ''), 10);
    return Number.isNaN(uid) ? null : uid;
});

const dateMin = computed(() => {
    return route.query.dateMin ? new Date(route.query.dateMin as string) : new Date(settings.date_min);
});
const dateMax = computed(() => {
    return route.query.dateMax ? new Date(route.query.dateMax as string) : getNow();
});

const options = computed(() => (vendeurUid.value === null ? undefined : { path: { uid: vendeurUid.value } }));

const { etat, refetch } = useReactiveFetch(getStructure, options);

const vendeur = computed(() => (etat.value.statut === 'succes' ? etat.value.data : null));
</script>

<template>
    <main className="card">
        <ErreurChargement v-if="etat.statut === 'erreur'" :erreur="etat.erreur" message="Le chargement de la fiche fournisseur a échoué" class="my-4" @retry="refetch" />

        <template v-else-if="vendeur">
            <h1>Tableau de bord du fournisseur : {{ structureName(vendeur) }}</h1>
            <p>Cette page vous présente les données essentielles des profils d'acheteurs ayant attribué des contrats au fournisseur {{ structureName(vendeur) }}, enrichies avec des données complémentaires.</p>
            <DetailsFournisseur :vendeur />
            <FiltreDates :dateMin :dateMax />
            <IndicateursCles :vendeurUid :dateMin :dateMax />
            <CategoriePrincipaleDAchat :vendeurUid :dateMin :dateMax />
            <Top12 type="acheteurs" :vendeurUid :dateMin :dateMax />
            <CarteAcheteursFournisseurs :vendeur :dateMin :dateMax />
            <DistributionTemporelleMarches :vendeurUid :dateMin :dateMax />
            <ListeMarches :vendeurUid :dateMin :dateMax />
            <NatureContrats :vendeurUid :dateMin :dateMax />
            <Procedure :vendeurUid :dateMin :dateMax />
            <AchatDurable :vendeurUid :dateMin :dateMax />
            <ListeConcessions :concessionnaireUid="vendeurUid" :dateMin :dateMax />
        </template>

        <ChargementEnCours v-else class="my-4" />
    </main>
</template>
