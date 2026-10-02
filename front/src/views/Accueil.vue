<script setup lang="ts">
import { getConf } from '@/client';
import AchatDurable from '@/components/dashboard/AchatDurable.vue';
import CategoriePrincipaleDAchat from '@/components/dashboard/CategoriePrincipaleDAchat.vue';
import Departements from '@/components/dashboard/Departements.vue';
import DistributionAchatsParDepartement from '@/components/dashboard/DistributionAchatsParDepartement.vue';
import IndicateursCles from '@/components/dashboard/IndicateursCles.vue';
import NatureContrats from '@/components/dashboard/NatureContrats.vue';
import Procedure from '@/components/dashboard/Procedure.vue';
import Top12 from '@/components/dashboard/Top12.vue';
import { formatDate, getNow, getOpsnRegion } from '@/service/HelpersService';
import { useReactiveFetch } from '@/utils/query';
import { computed } from 'vue';

const dateMin = new Date(settings.date_min);
const dateMax = getNow();

const { etat } = useReactiveFetch(
    getConf,
    computed(() => ({}))
);

const dernierImport = computed(() => (etat.value.statut === 'succes' ? etat.value.data.dernier_import : null));
</script>

<template>
    <main className="card">
        <h1>Données essentielles des marchés publics de la plateforme {{ getOpsnRegion() }}</h1>
        <div>
            <RouterLink to="/a-propos">
                <Button icon="pi pi-fw pi-info-circle" label="A propos de Focus Marchés v2" aria-label="A propos de Focus Marchés v2" severity="primary" size="small"></Button>
            </RouterLink>
            <Badge v-if="dernierImport" class="ml-5" severity="info" size="large"><i class="pi pi-fw pi-sync mr-2"></i> Données mises à jour le le {{ formatDate(new Date(dernierImport)) }}</Badge>
        </div>
        <IndicateursCles :dateMin :dateMax />
        <CategoriePrincipaleDAchat :dateMin :dateMax />
        <Top12 type="acheteurs" :dateMin :dateMax />
        <Top12 type="fournisseurs" :dateMin :dateMax />
        <NatureContrats :dateMin :dateMax />
        <Procedure :dateMin :dateMax />
        <AchatDurable :dateMin :dateMax />
        <Departements :dateMin :dateMax />
        <DistributionAchatsParDepartement :dateMin :dateMax />
    </main>
</template>
