<script setup>
import Acheteurs from '@/components/Acheteurs.vue';
</script>

<template>
    <div className="card">
        <h1>Les organismes du profil d'acheteur de Mégalis Bretagne</h1>
        <p>Cliquez sur chaque élement de la liste pour découvrir le profil détaillé de l'acheteur. Le montant affiché correspond au total des marchés passés par cet acheteur. La table est triée alphabetiquement par les organismes.</p>
        <Acheteurs />
    </div>
</template>
