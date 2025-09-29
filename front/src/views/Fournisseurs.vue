<script setup lang="ts">
import { listVendeursStructureVendeurGet } from '@/client';
import { formatCurrency } from '@/service/HelpersService';
import { FilterMatchMode } from '@primevue/core/api';
import { onMounted, ref } from 'vue';

const filters = ref({
    global: { value: null, matchMode: FilterMatchMode.CONTAINS },
    'structure.identifiant': { value: null, matchMode: FilterMatchMode.IN },
    nb_contrats: { value: null, matchMode: FilterMatchMode.EQUALS },
    montant: { value: null, matchMode: FilterMatchMode.EQUALS }
});

const fournisseurs = ref([]);

onMounted(() => {
    listVendeursStructureVendeurGet().then((response) => {
        fournisseurs.value = response.data;
    });
});
</script>

<template>
    <div className="card">
        <h1>Les fournisseurs répertoriés dans les profils d'acheteur de Mégalis Bretagne</h1>
        <p>Cliquez sur chaque élement de la liste pour découvrir le profil détaillé du titulaire. Le montant affiché correspond au total des contrats gagnés par le titulaire. La table est triée alphabetiquement par la dénomination des titulaires.</p>
        <DataTable
            :value="fournisseurs"
            v-model:filters="filters"
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
            <Column field="structure.identifiant" header="Annuaire">
                <template #body="slotProps">
                    <Button icon="pi pi-search" aria-label="Annuaire" as="a" :href="'https://annuaire-entreprises.data.gouv.fr/etablissement/' + slotProps.data.structure.identifiant" target="_blank" rel="noopener" />
                </template>
            </Column>
            <Column field="structure" header="Nom" sortable>
                <template #body="slotProps">
                    <RouterLink :to="'/fournisseur/' + slotProps.data.structure.uid">{{ slotProps.data.structure.nom }} {{ slotProps.data.structure.identifiant }} </RouterLink>
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
