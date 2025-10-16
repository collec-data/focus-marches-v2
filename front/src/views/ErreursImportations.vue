<script setup lang="ts">
import { getErreursImportErreursImportGet, getStatsErreursErreursImportStatsGet } from '@/client';
import { onMounted, ref } from 'vue';

import type { DecpMalFormeDtoOutput, StatsErreursDto } from '@/client';

const stats = ref<Array<StatsErreursDto>>([]);
const listDecpMalFormes = ref<Array<DecpMalFormeDtoOutput>>([]);

onMounted(() => {
    getErreursImportErreursImportGet({ query: { limit: 50 } }).then((response) => {
        if (response.data) {
            listDecpMalFormes.value = response.data;
        }
    });
    getStatsErreursErreursImportStatsGet().then((response) => {
        if (response.data) {
            stats.value = response.data;
        }
    });
});
</script>

<template>
    <main className="card">
        <h1>Erreurs lors de l'importation</h1>
        <div>
            <h2>Statistiques</h2>
            <DataTable :value="stats" scrollable scrollHeight="30rem" sortField="nombre" :sortOrder="-1">
                <Column field="localisation" header="Champs" sortable></Column>
                <Column field="erreur" header="Erreur" sortable></Column>
                <Column field="nombre" header="Nombre" sortable></Column>
            </DataTable>
        </div>
        <div class="mt-10">
            <h2>DECPs en erreur</h2>
            <Panel v-for="decp in listDecpMalFormes" :key="decp.uid">
                <ul>
                    <li v-for="erreur in decp.erreurs" :key="erreur.uid">
                        <Message severity="error"> [{{ erreur.type }}] {{ erreur.message }} - {{ erreur.localisation }} </Message>
                    </li>
                </ul>
                <pre>
                        <code>
                            {{ decp.decp }}
                        </code>
                    </pre>
            </Panel>
        </div>
    </main>
</template>
