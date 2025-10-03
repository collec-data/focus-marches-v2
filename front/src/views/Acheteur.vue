<script setup lang="ts">
import type { StructureEtendueDto } from '@/client';
import { getStructureStructureUidGet } from '@/client';
import { onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const acheteurUid = route.params.uid as string;

const acheteur = ref<Partial<StructureEtendueDto>>({});

onMounted(() => {
    getStructureStructureUidGet({ path: { uid: parseInt(acheteurUid) } }).then((response) => {
        if (response.data) {
            acheteur.value = response.data;
        }
    });
});
</script>

<template>
    <section className="card">
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

        <IndicateursCles :acheteurUid="acheteurUid" />
        <ListeMarches :acheteurUid="acheteurUid" />
        <NatureContrats :acheteurUid="acheteurUid" />
        <CCAG :acheteurUid="acheteurUid" />
        <Procedure :acheteurUid="acheteurUid" />
    </section>
</template>
