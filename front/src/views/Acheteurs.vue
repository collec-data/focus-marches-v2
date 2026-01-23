<script setup lang="ts">
import { listAcheteurs } from '@/client';
import { exportStructuresCSV, exportStructuresPdf } from '@/service/ExportDatatableService';
import { formatCurrency, formatNumber, getOpsnRegion, structureName } from '@/service/HelpersService';
import { onMounted, ref } from 'vue';

import type { StructureAggMarchesDto, StructuresAggChamps } from '@/client';
import { rowsPerPageOptions, useApiSideDataTable } from '@/service/DataTableHelper';

const acheteurs = ref<Array<StructureAggMarchesDto>>([]);

const { search, totalRecords, loading, rows, page, first, sortOrder, sortField, onPageChange, onSort } = useApiSideDataTable(fetchData);

function fetchData() {
    loading.value = true;
    listAcheteurs({
        query: {
            limit: rows.value,
            offset: page.value * rows.value,
            ordre: sortOrder.value,
            champs_ordre: sortField.value as StructuresAggChamps,
            filtre: search.value.toUpperCase()
        }
    }).then((response) => {
        if (response.data) {
            acheteurs.value = response.data.items;
            totalRecords.value = response.data.total;
        }
        loading.value = false;
    });
}

onMounted(() => {
    fetchData();
});

async function fetchAndExportAllData() {
    const response = await listAcheteurs({
        query: {
            ordre: sortOrder.value,
            champs_ordre: sortField.value as StructuresAggChamps,
            filtre: search.value.toUpperCase()
        }
    });
    return response.data;
}

async function exportCSV() {
    const data = await fetchAndExportAllData();
    if (data) {
        exportStructuresCSV(data.items, 'fournisseurs');
    }
}
async function exportPDF() {
    const data = await fetchAndExportAllData();
    if (data) {
        exportStructuresPdf(data.items, 'Liste des fournisseurs du profil acheteur de ' + getOpsnRegion(), 'fournisseurs');
    } else {
        console.error("La liste complète des acheteurs n'a pas pu être récupérée");
    }
}
</script>

<template>
    <main className="card">
        <h1>Les organismes du profil d'acheteur de {{ getOpsnRegion() }}</h1>
        <p>Cliquez sur chaque élement de la liste pour découvrir le profil détaillé de l'acheteur. Le montant affiché correspond au total des marchés passés par cet acheteur. La table est triée alphabetiquement par les organismes.</p>
        <DataTable
            :value="acheteurs"
            stripedRows
            paginator
            lazy
            :loading
            :rows
            :rowsPerPageOptions
            :totalRecords
            :first
            :sortField
            :sortOrder
            @page="(onPageChange($event), fetchData())"
            @update:rows="rows = $event"
            @sort="(onSort($event), fetchData())"
        >
            <template #header>
                <div class="flex flex-row">
                    <div class="basis-1/2">
                        <div class="basis-1/2 flex gap-1">
                            <Button icon="pi pi-file-excel" label="CSV" severity="secondary" size="small" @click="exportCSV()" />
                            <Button icon="pi pi-file-pdf" label="PDF" severity="secondary" size="small" @click="exportPDF()" />
                        </div>
                    </div>
                    <div class="basis-1/2 flex justify-end">
                        <IconField class="w-fit">
                            <InputIcon>
                                <i class="pi pi-search" />
                            </InputIcon>
                            <InputText v-model="search" placeholder="Nom ou SIRET" />
                        </IconField>
                    </div>
                </div>
            </template>
            <Column field="nom" header="Nom" sortable>
                <template #body="slotProps">
                    <RouterLink :to="'/acheteur/' + slotProps.data.structure.uid">
                        <Button :label="structureName(slotProps.data.structure)" as="a" variant="link" />
                    </RouterLink>
                </template>
            </Column>
            <Column field="nb_contrats" header="NB contrats" sortable>
                <template #body="{ data }">
                    {{ formatNumber(data.nb_contrats) }}
                </template>
            </Column>
            <Column field="montant" header="Montant contrats" sortable bodyStyle="text-align:right">
                <template #body="{ data }">
                    {{ formatCurrency(parseFloat(data.montant)) }}
                </template></Column
            >
        </DataTable>
    </main>
</template>
