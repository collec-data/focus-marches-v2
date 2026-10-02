<script setup lang="ts">
import { getErreursImport, getStatsErreurs } from '@/client';
import { computed, ref, toRaw, watch } from 'vue';

import type { StructureDto } from '@/client';
import StructureSearchAutoComplete from '@/components/StructureSearchAutoComplete.vue';
import { formatDate, formatNumber, getMonthAsString, getNow, structureName } from '@/service/HelpersService';
import { useStructureIdentifiee } from '@/service/UseStructureIdentifiee';
import { useReactiveFetch } from '@/utils/query';
import { useRoute, useRouter } from 'vue-router';

const router = useRouter();
const route = useRoute();

type Filtres = { acheteur: StructureDto | undefined; date_min: Date; date_max: Date };

function toDate(date: Date): Date {
    date.setUTCHours(0, 0, 0, 0);
    return date;
}

const filtres = ref<Filtres>({
    acheteur: undefined,
    date_min: route.query.dateMin ? new Date(route.query.dateMin as string) : new Date(settings.date_min),
    date_max: route.query.dateMax ? new Date(route.query.dateMax as string) : getNow()
});

const uidDepuisUrl = computed(() => {
    const uid = route.query.uid_structure;
    return uid ? parseInt(uid as string) : undefined;
});

// Seule la structure nommée dans l'URL est résolue : elle sert à préremplir le champ, pas à filtrer.
const { structure: structureDepuisUrl } = useStructureIdentifiee(uidDepuisUrl, () => null);

watch(structureDepuisUrl, (structure) => {
    if (structure) {
        filtres.value.acheteur = { ...structure, nom: structureName(structure) };
    }
});

// Le contexte demandé est celui validé par « Filtrer », jamais la saisie en cours.
const contexte = ref<Filtres>(structuredClone(toRaw(filtres.value)));

const statsOptions = computed(() => ({
    query: {
        date_debut: toDate(contexte.value.date_min),
        date_fin: toDate(contexte.value.date_max),
        uid_structure: contexte.value.acheteur?.uid
    }
}));

const { etat: etatStats, refetch: refetchStats } = useReactiveFetch(getStatsErreurs, statsOptions);

const stats = computed(() => (etatStats.value.statut === 'succes' ? etatStats.value.data : []));

/** L'erreur choisie dans le tableau des statistiques. `null` tant que rien n'est choisi. */
const selection = ref<{ localisation: string; type: string } | null>(null);

const decpsOptions = computed(() => {
    const choisie = selection.value;
    if (!choisie) {
        return undefined;
    }
    return {
        query: {
            localisation: choisie.localisation,
            type: choisie.type,
            date_debut: toDate(contexte.value.date_min),
            date_fin: toDate(contexte.value.date_max),
            uid_structure: contexte.value.acheteur?.uid
        }
    };
});

const { etat: etatDecps, refetch: refetchDecps } = useReactiveFetch(getErreursImport, decpsOptions);

const listDecpMalFormes = computed(() => (etatDecps.value.statut === 'succes' ? etatDecps.value.data : []));

function loadDecps(localisation: string, type: string) {
    selection.value = { localisation, type };
}

function search() {
    router.push({
        name: route.name,
        params: route.params,
        query: {
            ...route.query,
            dateMin: getMonthAsString(filtres.value.date_min),
            dateMax: getMonthAsString(filtres.value.date_max),
            uid_structure: filtres.value.acheteur?.uid
        }
    });
    // Un nouveau contexte rend les DECPs affichés caducs : ils appartenaient au précédent.
    selection.value = null;
    contexte.value = structuredClone(toRaw(filtres.value));
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
            <ErreurChargement v-if="etatStats.statut === 'erreur'" :erreur="etatStats.erreur" message="Le chargement des statistiques a échoué" class="my-4" @retry="refetchStats" />
            <DataTable :value="stats" scrollable scrollHeight="30rem" sortField="nombre" :sortOrder="-1" :loading="etatStats.statut === 'chargement'">
                <template v-if="etatStats.statut === 'succes'" #empty>
                    <div class="text-center">
                        <Badge size="xlarge" severity="info">Aucune erreur</Badge>
                    </div>
                </template>
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
            <p v-if="!selection">Clique sur la loupe d'une erreur dans le tableau ci-dessus pour afficher les DECPs concernés</p>
            <ErreurChargement v-else-if="etatDecps.statut === 'erreur'" :erreur="etatDecps.erreur" message="Le chargement des DECPs en erreur a échoué" class="my-4" @retry="refetchDecps" />
            <ChargementEnCours v-else-if="etatDecps.statut === 'chargement'" class="my-4" libelle="Chargement des DECPs en erreur" />
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
