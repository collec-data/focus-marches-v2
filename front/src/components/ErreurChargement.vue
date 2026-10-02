<script setup lang="ts">
import type { ErreurReactiveFetch } from '@/utils/query';
import { computed } from 'vue';

const props = withDefaults(
    defineProps<{
        erreur: ErreurReactiveFetch;
        /** Remplace le message par défaut, lorsqu'un échec ne se explique pas par la requête elle-même. */
        message?: string;
    }>(),
    { message: 'Le chargement a échoué' }
);

defineEmits<{ retry: [] }>();

/** Retenter ne peut aboutir que sur une panne : une référence inconnue ou un paramètre invalide le resterait. */
const rejouable = computed(() => props.erreur.nature === 'technique');
</script>

<template>
    <Message :closable="false" severity="error">
        <span>{{ message }}</span>
        <Button v-if="rejouable" class="ml-3" label="Réessayer" severity="error" size="small" variant="text" @click="$emit('retry')" />
    </Message>
</template>
