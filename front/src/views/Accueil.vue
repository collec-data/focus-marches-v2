<script setup lang="ts">
import CategoriePrincipaleDAchat from '@/components/dashboard/CategoriePrincipaleDAchat.vue';
import Departements from '@/components/dashboard/Departements.vue';
import DistributionAchatsParDepartement from '@/components/dashboard/DistributionAchatsParDepartement.vue';
import IndicateursCles from '@/components/dashboard/IndicateursCles.vue';
import NatureContrats from '@/components/dashboard/NatureContrats.vue';
import Procedure from '@/components/dashboard/Procedure.vue';
import Top12 from '@/components/dashboard/Top12.vue';
import { getNow, getOpsnRegion } from '@/service/HelpersService';

const dateMin = new Date(settings.date_min);
const dateMax = getNow();
const region = settings.region;
const opsn = settings.opsn;
</script>

<template>
    <main className="card">
        <h1>Données essentielles des marchés publics de la plateforme {{ getOpsnRegion() }}</h1>
        <p>
            Cet outil exploite les données essentielles des marchés publics passés en {{ region }} sous réserves que l'organisme qui passe le marché public soit adhérent au service proposé par {{ opsn }} et qu'il ait bien complété toutes les
            informations nécessaires dans la salle des marchés publics (bien renseigné l'étape décision). On ne trouvera pas, par exemple, les marchés des services de l'Etat qui utilisent leur propre plateforme.
        </p>
        <IndicateursCles :dateMin :dateMax />
        <CategoriePrincipaleDAchat :dateMin :dateMax />
        <Top12 type="acheteurs" :dateMin :dateMax />
        <Top12 type="fournisseurs" :dateMin :dateMax />
        <NatureContrats :dateMin :dateMax />
        <Procedure :dateMin :dateMax />
        <Departements :dateMin :dateMax />
        <DistributionAchatsParDepartement :dateMin :dateMax />
    </main>
</template>
