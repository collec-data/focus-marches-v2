<script setup lang="ts">
import type { PropType } from 'vue';
import { getNow, structureName } from '@/service/HelpersService';
import { useStructureIdentifiee } from '@/service/UseStructureIdentifiee';
import { computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const props = defineProps({
    siret: { type: String as PropType<string | null>, required: false }
});

const dateMin = computed(() => {
    return route.query.dateMin ? new Date(route.query.dateMin as string) : new Date(settings.date_min);
});
const dateMax = computed(() => {
    return route.query.dateMax ? new Date(route.query.dateMax as string) : getNow();
});

// L'uid est lu dans l'URL s'il y en a un ; sinon la route ne demande que le SIRET, et l'identité se résout.
const uidDepuisUrl = computed(() => {
    const uid = Number.parseInt(String(route.params.uid ?? ''), 10);
    return Number.isNaN(uid) ? null : uid;
});

const { uid: acheteurUid, structure: acheteur, erreur: erreurIdentite, refetch: refetchIdentite } = useStructureIdentifiee(uidDepuisUrl, () => props.siret ?? null, { structure: true });

const acheteurSiret = computed(() => acheteur.value?.identifiant ?? null);

const show = !route.path.includes('widget');
const domain = window.location.origin;
</script>

<template>
    <main className="card">
        <ErreurChargement v-if="erreurIdentite" :erreur="erreurIdentite" message="Aucune structure ne correspond à ce SIRET" class="my-4" @retry="refetchIdentite" />
        <ChargementEnCours v-else-if="acheteurUid === undefined" class="my-4" />
        <template v-else-if="acheteur">
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
            <DistributionTemporelleMarches :acheteurUid :dateMax :dateMin />
            <ListeMarches :acheteurUid :dateMax :dateMin />
            <NatureContrats :acheteurUid :dateMax :dateMin />
            <CCAG :acheteurUid :dateMax :dateMin />
            <Procedure :acheteurUid :dateMax :dateMin />
            <AchatDurable :acheteurUid :dateMax :dateMin />
            <ListeConcessions :autoriteConcedanteUid="acheteurUid" :dateMax :dateMin />
        </template>
    </main>
</template>
