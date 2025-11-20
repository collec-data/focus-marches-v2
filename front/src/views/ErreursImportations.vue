<script setup lang="ts">
import { getErreursImport, getStatsErreurs } from '@/client';
import { onMounted, ref } from 'vue';

import type { DecpMalFormeDto, StatsErreursDto } from '@/client';
import { formatNumber } from '@/service/HelpersService';

const stats = ref<Array<StatsErreursDto>>([]);
const listDecpMalFormes = ref<Array<DecpMalFormeDto>>([]);

onMounted(() => {
    getStatsErreurs().then((response) => {
        if (response.data) {
            stats.value = response.data;
        }
    });
});

function loadDecps(localisation: string, type: string) {
    console.log(type);
    getErreursImport({ query: { localisation: localisation, type: type } }).then((response) => {
        if (response.data) {
            listDecpMalFormes.value = response.data;
        }
    });
}
</script>

<template>
    <main className="card">
        <h1>Erreurs lors de l'importation</h1>
        <div>
            <h2>Statistiques</h2>
            <DataTable :value="stats" scrollable scrollHeight="30rem" sortField="nombre" :sortOrder="-1">
                <Column header="DECPs">
                    <template #body="{ data }">
                        <Button icon="pi pi-search" severity="secondary" aria-label="Voir les DECPs concernés par cette erreur" @click="loadDecps(data.localisation, data.type)" />
                    </template>
                </Column>
                <Column field="localisation" header="Champs" sortable></Column>
                <Column field="erreur" header="Erreur" sortable></Column>
                <Column field="nombre" header="Nombre" sortable>
                    <template #body="{ data }">
                        {{ formatNumber(data.nombre) }}
                    </template>
                </Column>
            </DataTable>
        </div>
        <div class="mt-10">
            <h2>DECPs en erreur</h2>
            <p v-if="!listDecpMalFormes.length">Clique sur la loupe d'une erreur dans le tableau ci-dessus pour afficher les DECPs concernés</p>
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
