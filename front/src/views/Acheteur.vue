<script setup>
import Acheteur from '@/components/Acheteur.vue';
import { useRoute } from 'vue-router';

const route = useRoute();
</script>

<template>
    <Acheteur :acheteur_id="route.params.id" />
</template>
