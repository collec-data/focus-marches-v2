<script setup lang="ts">
defineProps({
    /** Ce qui est en cours de chargement, annoncé aux technologies d'assistance. */
    libelle: { type: String, default: 'Chargement en cours' }
});
</script>

<template>
    <div class="text-center">
        <ProgressSpinner :aria-label="libelle" style="width: 5rem; height: 5rem" />
    </div>
</template>
