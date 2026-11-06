<script setup lang="ts">
defineProps<{
    /** La limite de résultats, ou `null` quand elle n'est pas atteinte. */
    limite: number | null;
}>();
</script>

<template>
    <Message v-if="limite !== null" severity="warn" :closable="false" class="my-4">Le nombre de résultats affichés est limité aux {{ limite }} plus récents. Veuillez affiner vos filtres.</Message>
</template>
