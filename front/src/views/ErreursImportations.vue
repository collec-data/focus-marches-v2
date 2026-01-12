<script setup lang="ts">
import { getErreursImport, getStatsErreurs, getStructure } from '@/client';
import { onMounted, ref } from 'vue';

import type { DecpMalFormeDto, StatsErreursDto, StructureDto } from '@/client';
import StructureSearchAutoComplete from '@/components/StructureSearchAutoComplete.vue';
import { formatDate, formatNumber, getNow, structureName } from '@/service/HelpersService';
import { useRoute, useRouter } from 'vue-router';

const router = useRouter();
const route = useRoute();

const stats = ref<Array<StatsErreursDto>>([]);
const listDecpMalFormes = ref<Array<DecpMalFormeDto>>([]);

const filtres = ref({
    acheteur: undefined as undefined | StructureDto,
    date_min: route.query.dateMin ? new Date(route.query.dateMin as string) : new Date(settings.date_min),
    date_max: route.query.dateMax ? new Date(route.query.dateMax as string) : getNow()
});

function toDate(date: Date | null): Date | null {
    if (date) {
        date.setUTCHours(0, 0, 0, 0);
    }
    return date;
}

function fetchStats() {
    getStatsErreurs({
        query: {
            date_debut: toDate(filtres.value.date_min),
            date_fin: toDate(filtres.value.date_max),
            uid_structure: filtres.value.acheteur?.uid
        }
    }).then((response) => {
        if (response.data) {
            stats.value = response.data;
        }
    });
}

onMounted(() => {
    if (route.query.uid_structure) {
        getStructure({ path: { uid: parseInt(route.query.uid_structure as string) } }).then((response) => {
            if (response.data) {
                filtres.value.acheteur = { ...response.data, nom: structureName(response.data) };
            }
        });
    }
    fetchStats();
});

function loadDecps(localisation: string, type: string) {
    getErreursImport({
        query: {
            localisation: localisation,
            type: type,
            date_debut: toDate(filtres.value.date_min),
            date_fin: toDate(filtres.value.date_max),
            uid_structure: filtres.value.acheteur?.uid
        }
    }).then((response) => {
        if (response.data) {
            listDecpMalFormes.value = response.data;
        }
    });
}

function search() {
    const query = {
        ...route.query,
        dateMin: filtres.value.date_min ? filtres.value.date_min.toISOString().substring(0, 10) : undefined,
        dateMax: filtres.value.date_max ? filtres.value.date_max.toISOString().substring(0, 10) : undefined,
        uid_structure: filtres.value.acheteur ? filtres.value.acheteur.uid : undefined
    };
    router.push({
        name: route.name,
        params: route.params,
        query: query
    });
    listDecpMalFormes.value = [];
    fetchStats();
}
</script>

<template>
    <main className="card">
        <h1>Erreurs lors de l'importation</h1>
        <Panel header="Filtrer les erreurs d'importation (optionnel)" class="mb-5">
            <form @submit.prevent="search">
                <div class="flex flex-row gap-5 mb-5">
                    <div class="basis-1/3">
                        <StructureSearchAutoComplete v-model="filtres.acheteur" structureType="acheteur" />
                    </div>
                    <div class="basis-1/3">
                        <label for="date_min">Date min.</label>
                        <DatePicker v-model="filtres.date_min" inputId="date_min" name="date_min" updateModelType="date" showIcon showButtonBar fluid />
                    </div>
                    <div class="basis-1/3">
                        <label for="date_max">Date max.</label>
                        <DatePicker v-model="filtres.date_max" inputId="date_max" name="date_max" updateModelType="date" showIcon showButtonBar fluid />
                    </div>
                </div>
                <Button class="uppercase w-full" type="submit" label="Filtrer" severity="secondary" />
            </form>
        </Panel>
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
                <template #header>
                    <Badge severity="info" size="large">{{ decp.structure ? structureName(decp.structure) : '' }}</Badge>
                    <Badge severity="secondary" size="large">{{ decp.date_creation ? formatDate(decp.date_creation) : '' }}</Badge>
                </template>
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
