<script setup>
import { useRoute } from 'vue-router';

const route = useRoute();
</script>

<template>
    <section className="card">
        <h1>Tableau de bord de l'acheteur :</h1>
        <p>Cette page vous présente les données essentielles du profil d'acheteur de Aqua Ouest , enrichies avec des données complémentaires.</p>

        <h2>Localisation et contexte</h2>

        <IndicateursCles :acheteur_uid="route.params.uid" />
        <Procedure :acheteur_uid="route.params.uid" />
    </section>
</template>
