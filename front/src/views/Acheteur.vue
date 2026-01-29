<script setup lang="ts">
import type { StructureEtendueDto } from '@/client';
import { getStructure, getStructureId } from '@/client';
import { getNow, structureName } from '@/service/HelpersService';
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const acheteurUid = ref(parseInt(route.params.uid as string) || -1);
const acheteurSiret = computed(() => acheteur?.value.identifiant);
const acheteur = ref<Partial<StructureEtendueDto>>({});
/* Définir acheteurUid à -1 permet de dire aux composants inférieurs d'attendre que le SIRET soit transformé en uid avant de se générer.
Cela évite le cas où l'on charge TOUS les marchés de la plateforme parce que l'acheteurUid n'est pas encore défini et ne peut donc rien filtrer */

const props = defineProps({
    siret: { type: [String, null], default: null }
});

const dateMin = computed(() => {
    return route.query.dateMin ? new Date(route.query.dateMin as string) : new Date(settings.date_min);
});
const dateMax = computed(() => {
    return route.query.dateMax ? new Date(route.query.dateMax as string) : getNow();
});

function fetchData() {
    if (props.siret) {
        getStructureId({ path: { id: props.siret, type_id: 'SIRET' } }).then((response) => {
            if (response.data) {
                acheteur.value = response.data;
                acheteurUid.value = response.data.uid;
            }
        });
    } else {
        getStructure({ path: { uid: acheteurUid.value } }).then((response) => {
            if (response.data) {
                acheteur.value = response.data;
            }
        });
    }
}

watch(acheteurUid, () => {
    fetchData();
});

onMounted(() => {
    fetchData();
});

const show = !route.path.includes('widget');
const domain = window.location.origin;
</script>

<template>
    <main className="card">
        <h1>Tableau de bord de l'acheteur : {{ structureName(acheteur) }}</h1>
        <p>Cette page vous présente les données essentielles du profil d'acheteur de {{ structureName(acheteur) }} , enrichies avec des données complémentaires.</p>

        <details v-if="show">
            <summary><i class="pi pi-code"></i> Intégrer la page à son site</summary>
            <div>
                <p>Copier le code ci-dessous pour intégrer cette page à votre site internet, ainsi les données du tableau de bord seront visibles sur votre site et mises à jour automatiquement.</p>
                <pre>
                    <code>{{  '\n<iframe \n\tsrc="'  + domain + '/widget/acheteur/' + acheteur.identifiant + '" \n\treferrerpolicy="strict-origin-when-cross-origin" \n\tstyle="border: 0; overflow: hidden;" \n\ttitle="Tableau de bord de l\'acheteur '+ structureName(acheteur) + '"\n></iframe>'  }}</code>
                </pre>
                <p>
                    Configuration : Selon vos besoins sur votre site ajoutez les attributs <code>{{ 'width=""' }}</code> et <code>{{ 'heigth=""' }}</code> avec les valeurs appropriés.
                </p>
            </div>
        </details>
        <DetailsAcheteur :acheteur />
        <FiltreDates :dateMin :dateMax />
        <IndicateursCles :acheteurUid :acheteurSiret :dateMin :dateMax />
        <CategoriePrincipaleDAchat :acheteurUid :acheteurSiret :dateMin :dateMax />
        <Top12 type="fournisseurs" :acheteurUid :acheteurSiret :dateMin :dateMax />
        <CarteAcheteursFournisseurs :acheteur :acheteurSiret :dateMin :dateMax />
        <DistributionTemporelleMarches :acheteurUid :acheteurSiret :dateMin :dateMax />
        <ListeMarches :nomStructure="structureName(acheteur)" :acheteurUid :acheteurSiret :dateMin :dateMax />
        <NatureContrats :acheteurUid :acheteurSiret :dateMin :dateMax />
        <CCAG :acheteurUid :acheteurSiret :dateMin :dateMax />
        <Procedure :acheteurUid :acheteurSiret :dateMin :dateMax />
        <AchatDurable :acheteurUid :acheteurSiret :dateMin :dateMax />
        <ListeConcessions :autoriteConcedanteUid="acheteurUid" :autoriteConcedanteSiret="acheteurSiret" :dateMin :dateMax />
    </main>
</template>
