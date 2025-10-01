<script setup lang="ts">
import { listAcheteursStructureAcheteurGet } from '@/client';
import { formatCurrency } from '@/service/HelpersService';
import { FilterMatchMode } from '@primevue/core/api';
import { onMounted, ref } from 'vue';

const filters = ref({
    global: { value: null, matchMode: FilterMatchMode.CONTAINS },
    'structure.identifiant': { value: null, matchMode: FilterMatchMode.IN },
    nb_contrats: { value: null, matchMode: FilterMatchMode.EQUALS },
    montant: { value: null, matchMode: FilterMatchMode.EQUALS }
});

const acheteurs = ref([]);

onMounted(() => {
    listAcheteursStructureAcheteurGet().then((response) => {
        acheteurs.value = response.data;
    });
});
</script>

<template>
    <div className="card">
        <h1>Les organismes du profil d'acheteur de Mégalis Bretagne</h1>
        <p>Cliquez sur chaque élement de la liste pour découvrir le profil détaillé de l'acheteur. Le montant affiché correspond au total des marchés passés par cet acheteur. La table est triée alphabetiquement par les organismes.</p>
        <DataTable
            v-model:filters="filters"
            :value="acheteurs"
            :globalFilterFields="['structure.identifiant', 'montant', 'nb_contrats']"
            sortField="structure.identifiant"
            :sortOrder="1"
            removableSort
            stripedRows
            filterDisplay="row"
            paginator
            :rows="25"
            :rowsPerPageOptions="[10, 25, 50]"
        >
            <template #header>
                <div class="flex flex-row">
                    <div class="basis-1/2">
                        <Button disabled icon="pi pi-external-link" label="Export" />
                    </div>
                    <div class="basis-1/2 flex justify-end">
                        <IconField class="w-fit">
                            <InputIcon>
                                <i class="pi pi-search" />
                            </InputIcon>
                            <InputText v-model="filters['global'].value" placeholder="Keyword Search" />
                        </IconField>
                    </div>
                </div>
            </template>
            <Column field="structure.nom" header="Nom" sortable>
                <template #body="slotProps">
                    <RouterLink :to="'/acheteur/' + slotProps.data.structure.uid">
                        {{ slotProps.data.structure.nom }}
                    </RouterLink>
                </template>
            </Column>
            <Column field="nb_contrats" header="NB contrats" sortable></Column>
            <Column field="montant" header="Montant contrats" sortable bodyStyle="text-align:right">
                <template #body="{ data }">
                    {{ formatCurrency(data.montant) }}
                </template></Column
            >
        </DataTable>
    </div>
</template>
