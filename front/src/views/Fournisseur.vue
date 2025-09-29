<script setup lang="ts">
import { useRoute } from 'vue-router';

const route = useRoute();
</script>

<template>
    <section className="card">
        <h1>Tableau de bord du fournisseur :</h1>
        <p>Cette page vous présente les données essentielles des profils d'acheteurs ayant attribué des contrats au fournisseur "", enrichies avec des données complémentaires.</p>

        <h2>Localisation et contexte</h2>

        <IndicateursCles :vendeur_uid="route.params.uid as string" />
        <ListeMarches :vendeur_uid="route.params.uid as string" />
        <Procedure :vendeur_uid="route.params.uid as string" />
    </section>
</template>
