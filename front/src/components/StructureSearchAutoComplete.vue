<script setup lang="ts">
import { listStructures, type StructureDto } from '@/client';
import { StructureType } from '@/service/enums';
import { structureName } from '@/service/HelpersService';
import type { AutoCompleteCompleteEvent } from 'primevue';
import { computed, ref, useId } from 'vue';

const model = defineModel<StructureDto>();

const props = defineProps<{ structureType: StructureType }>();

const id = useId();
const name = computed(() => props.structureType);

const structures = ref<StructureDto[]>([]);
const filterOptions = {
    ignoreCase: true
};
function searchStructure(e: AutoCompleteCompleteEvent) {
    if (e.query.length > 1) {
        let nom = e.query.toUpperCase();
        if (nom.startsWith('SIRET')) {
            nom = nom.substring(6);
        }
        const query = { nom: nom };
        if (props.structureType == StructureType.Acheteur) {
            query['is_acheteur'] = true;
        }
        if (props.structureType == StructureType.Fournisseur) {
            query['is_vendeur'] = true;
        }
        listStructures({ query: query }).then((response) => {
            if (response.data) {
                structures.value = response.data.map((structure) => ({ ...structure, nom: structureName(structure) }));
            }
        });
    } else {
        structures.value = [];
    }
}
</script>

<template>
    <label :for="id" class="capitalize">{{ name }}</label>
    <AutoComplete v-model="model" :suggestions="structures" optionLabel="nom" :inputId="id" :name showClear fluid :filterOptions @complete="searchStructure" />
</template>
