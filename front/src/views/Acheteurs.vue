<script setup lang="ts">
import { listAcheteurs } from '@/client';
import { rowsPerPageOptions, useApiSideDataTable } from '@/service/DataTableHelper';
import { useEcritureDebouncee } from '@/service/Debouncer';
import { exportStructuresCSV, exportStructuresExcel, exportStructuresPdf } from '@/service/ExportDatatableService';
import { formatCurrency, formatNumber, getOpsnRegion, structureName } from '@/service/HelpersService';
import { ref } from 'vue';

import type { StructuresAggChamps } from '@/client';

const { filtre, page, totalRecords, loading, rows, first, sortOrder, sortField, onPageChange, onSort, items, etat, refetch } = useApiSideDataTable(listAcheteurs);

const search = ref('');

// La frappe n'interroge pas l'API : le terme envoyé à la liste est différé et normalisé comme le fait
// la recherche par structure, et un terme nouveau repart de la première page.
useEcritureDebouncee(
    () => search.value.toUpperCase(),
    filtre,
    () => {
        page.value = 0;
    }
);

async function fetchAndExportAllData() {
    const response = await listAcheteurs({
        query: {
            ordre: sortOrder.value,
            champs_ordre: sortField.value as StructuresAggChamps,
            filtre: filtre.value
        }
    });
    return response.data;
}

async function exportExcel() {
    const data = await fetchAndExportAllData();
    if (data) exportStructuresExcel(data.items, 'acheteurs');
    else console.error("La liste complète des acheteurs n'a pas pu être récupérée");
}

async function exportCSV() {
    const data = await fetchAndExportAllData();
    if (data) exportStructuresCSV(data.items, 'acheteurs');
    else console.error("La liste complète des acheteurs n'a pas pu être récupérée");
}

async function exportPDF() {
    const data = await fetchAndExportAllData();
    if (data) exportStructuresPdf(data.items, 'Liste des acheteurs du profil acheteur de ' + getOpsnRegion(), 'acheteurs');
    else console.error("La liste complète des acheteurs n'a pas pu être récupérée");
}
</script>

<template>
    <main className="card">
        <h1>Les organismes du profil d'acheteur de {{ getOpsnRegion() }}</h1>
        <p>
            Cliquez sur chaque élement de la liste pour découvrir le profil détaillé de l'acheteur. Le montant affiché correspond au total des marchés passés par cet acheteur. La table est triée alphabetiquement par les organismes. Certains acheteurs
            peuvent être classés en [ND] , c'est-à-dire en données non diffusables ou non diffusibles.
        </p>
        <ErreurChargement v-if="etat.statut === 'erreur'" :erreur="etat.erreur" message="Le chargement de la liste des acheteurs a échoué" class="my-4" @retry="refetch" />

        <DataTable :value="items" stripedRows paginator lazy :loading :rows :rowsPerPageOptions :totalRecords :first :sortField :sortOrder @page="onPageChange" @update:rows="rows = $event" @sort="onSort">
            <template #header>
                <div class="flex flex-row">
                    <div class="basis-1/2">
                        <div class="basis-1/2 flex gap-1">
                            <Button icon="pi pi-table" label="CSV" severity="secondary" size="small" @click="exportCSV()" />
                            <Button icon="pi pi-file-excel" label="Excel" severity="secondary" size="small" @click="exportExcel()" />
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
