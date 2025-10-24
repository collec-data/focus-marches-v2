<script setup lang="ts">
import Acheteurs from '@/components/dashboard/Acheteurs.vue';
import CategoriePrincipaleDAchat from '@/components/dashboard/CategoriePrincipaleDAchat.vue';
import Departements from '@/components/dashboard/Departements.vue';
import DistributionAchatsParDepartement from '@/components/dashboard/DistributionAchatsParDepartement.vue';
import IndicateursCles from '@/components/dashboard/IndicateursCles.vue';
import NatureContrats from '@/components/dashboard/NatureContrats.vue';
import Procedure from '@/components/dashboard/Procedure.vue';
</script>

<template>
    <main className="card">
        <h1>Données essentielles des marchés publics de la plateforme Mégalis Bretagne</h1>
        <p>
            Cet outil exploite les données essentielles des marchés publics passés en Bretagne sous réserves que l'organisme qui passe le marché public soit adhérent au service proposé par Mégalis Bretagne et qu'il ait bien complété toutes les
            informations nécessaires dans la salle des marchés publics (bien renseigné l'étape décision). On ne trouvera pas, par exemple, les marchés des services de l'Etat qui utilisent leur propre plateforme.
        </p>
        <IndicateursCles />
        <CategoriePrincipaleDAchat />
        <Acheteurs />
        <NatureContrats />
        <Procedure />
        <Departements />
        <DistributionAchatsParDepartement />
    </main>
</template>
