<script setup lang="ts">
import { listStructures, type ListStructuresData, type StructureDto } from '@/client';
import { structureName } from '@/service/HelpersService';
import { useReactiveFetch } from '@/utils/query';
import type { AutoCompleteCompleteEvent } from 'primevue';
import { computed, ref, useId } from 'vue';

const model = defineModel<StructureDto>();

const props = defineProps<{ structureType: 'acheteur' | 'fournisseur' }>();

const id = useId();
const name = computed(() => props.structureType);

const filterOptions = {
    ignoreCase: true
};

/** Saisie en cours. La recherche part dès qu'elle est exploitable, et repart à chaque frappe au-delà. */
const saisie = ref('');

const options = computed<{ query: NonNullable<ListStructuresData['query']> } | undefined>(() => {
    if (saisie.value.length <= 1) {
        return undefined;
    }
    let nom = saisie.value.toUpperCase();
    if (nom.startsWith('SIRET')) {
        nom = nom.substring(6);
    }
    return { query: { nom: nom, is_acheteur: props.structureType === 'acheteur', is_vendeur: props.structureType === 'fournisseur' } };
});

const { etat } = useReactiveFetch(listStructures, options);

const structures = computed<StructureDto[]>(() => (etat.value.statut === 'succes' ? etat.value.data.map((structure) => ({ ...structure, nom: structureName(structure) })) : []));

function searchStructure(e: AutoCompleteCompleteEvent) {
    saisie.value = e.query;
}
</script>

<template>
    <label :for="id" class="capitalize">{{ name }}</label>
    <AutoComplete v-model="model" :suggestions="structures" optionLabel="nom" :inputId="id" :name showClear fluid :filterOptions @complete="searchStructure" />
</template>
