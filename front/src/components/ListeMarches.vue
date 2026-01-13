<script setup lang="ts">
import { getListeMarches } from '@/client';
import { formatBoolean, formatCurrency, formatDate, getCatEntreprise, structureName } from '@/service/HelpersService';
import { FilterMatchMode } from '@primevue/core/api';
import { computed, onMounted, ref, watch } from 'vue';

import type { MarcheAllegeDto } from '@/client';

const props = defineProps({
    nomStructure: { type: String },
    acheteurUid: { type: [String, null], default: null },
    vendeurUid: { type: [String, null], default: null },
    dateMin: { type: [Date, null], default: null },
    dateMax: { type: [Date, null], default: null }
});

const filters = ref({
    global: { value: null, matchMode: FilterMatchMode.CONTAINS },
    cpv: { value: null, matchMode: FilterMatchMode.EQUALS },
    objet: { value: null, matchMode: FilterMatchMode.IN },
    'acheteur.nom': { value: null, matchMode: FilterMatchMode.IN },
    montant: { value: null, matchMode: FilterMatchMode.EQUALS }
});

const listeMarches = ref<Array<MarcheAllegeDto>>([]);

function fetchData() {
    getListeMarches({
        query: {
            date_debut: props.dateMin,
            date_fin: props.dateMax,
            acheteur_uid: props.acheteurUid,
            vendeur_uid: props.vendeurUid
        }
    }).then((response) => {
        if (response.data) {
            listeMarches.value = response.data;
        }
    });
}

onMounted(() => {
    fetchData();
});

watch([() => props.dateMin, () => props.dateMax, () => props.acheteurUid, () => props.vendeurUid], () => {
    fetchData();
});

const countSousTraitants = (value: Array<any>) => {
    return value.length ? value.length : '';
};

const marcheUid = ref(null);

const columns = ref([
    { field: 'cpv', header: 'CPV' },
    { field: 'sous_trait', header: 'Sous-trait.' },
    { field: 'nb_sous_traitant', header: 'Nb sous-traitants' },
    { field: 'cons_env', header: 'Cons. Env.' },
    { field: 'cons_soc', header: 'Cons. Soc.' },
    { field: 'ac', header: 'AC' }
]);
const selectedColumns = ref(columns.value);

const onToggle = (val) => {
    selectedColumns.value = columns.value.filter((col) => val.includes(col));
};

const hiddenCol = computed(() => {
    const selectedAsArray = new Set(
        selectedColumns.value.map((e) => {
            return e.field;
        })
    );
    return Object.fromEntries(columns.value.map((e) => [e.field, !selectedAsArray.has(e.field)]));
});
</script>

<template>
    <section>
        <h2 class="title">Tous les marchés de {{ nomStructure }}</h2>
        <p>Ce tableau affiche les principales informations des marchés de {{ nomStructure }}. Cliquez sur «&nbsp;Voir&nbsp;» pour accéder au détail de chaque marché.</p>
        <DataTable
            v-model:filters="filters"
            :value="listeMarches"
            sortField="date_notification"
            :sortOrder="-1"
            size="small"
            stripedRows
            paginator
            :rows="10"
            :rowsPerPageOptions="[10, 25, 50]"
            :pt="{ column: { headerCell: { style: 'font-size:0.8rem; text-transform:uppercase;' } } }"
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
                <div class="text-right">
                    <MultiSelect :modelValue="selectedColumns" :options="columns" optionLabel="header" display="chip" placeholder="Colones affichées" @update:modelValue="onToggle" />
                </div>
            </template>
            <Column header="Détails">
                <template #body="{ data }"> <Button label="Voir" aria-label="Voir les détails du marché" @click="marcheUid = data.uid" /> </template
            ></Column>
            <Column field="cpv" header="CPV" sortable :hidden="hiddenCol.cpv">
                <template #body="{ data }">{{ data.cpv.code + ' ' + data.cpv.libelle }}</template>
            </Column>
            <Column field="objet" header="Objet" sortable style="min-width: 20rem"></Column>
            <Column v-if="acheteurUid == null" field="acheteur.nom" header="Acheteur" sortable>
                <template #body="{ data }">{{ structureName(data.acheteur) }}</template>
            </Column>
            <Column header="Fournisseur">
                <template #body="{ data }">
                    <div v-for="titulaire in data.titulaires" :key="titulaire.uid">
                        {{ structureName(titulaire) }}&nbsp;<span v-tooltip="getCatEntreprise(titulaire.cat_entreprise)" class="text-sm">[{{ titulaire.cat_entreprise }}]</span>
                    </div>
                </template>
            </Column>
            <Column field="sous_traitance_declaree" sortable :hidden="hiddenCol.sous_trait">
                <template #header>
                    <span v-tooltip.bottom="'Sous-traitance déclarée'" class="p-datatable-column-title" data-pc-section="columntitle">Sous-Trait.</span>
                </template>
                <template #body="{ data }">
                    {{ formatBoolean(data.sous_traitance_declaree) }}
                </template>
            </Column>
            <Column field="actes_sous_traitance" header="Nb sous-traitants" sortable :hidden="hiddenCol.nb_sous_traitant">
                <template #body="{ data }">
                    {{ countSousTraitants(data.actes_sous_traitance) }}
                </template>
            </Column>
            <Column field="considerations_environnementales" sortable :hidden="hiddenCol.cons_env">
                <template #header>
                    <span v-tooltip.bottom="'Considérations environnementales'" class="p-datatable-column-title" data-pc-section="columntitle">Cons. Env.</span>
                </template>
                <template #body="{ data }">
                    {{ formatBoolean(data.considerations_environnementales?.length > 0) }}
                </template>
            </Column>
            <Column field="considerations_sociales" sortable :hidden="hiddenCol.cons_soc">
                <template #header>
                    <span v-tooltip.bottom="'Considérations sociales'" class="p-datatable-column-title" data-pc-section="columntitle">Cons. Soc.</span>
                </template>
                <template #body="{ data }">
                    {{ formatBoolean(data.considerations_sociales?.length > 0) }}
                </template>
            </Column>
            <Column field="date_notification" sortable>
                <template #header>
                    <span v-tooltip.bottom="'Date de notification'" class="p-datatable-column-title" data-pc-section="columntitle">Date de notif.</span>
                </template>
                <template #body="{ data }">
                    {{ formatDate(data.date_notification) }}
                </template>
            </Column>
            <Column field="montant" header="Montant" dataType="numeric" sortable>
                <template #body="{ data }">
                    {{ formatCurrency(parseFloat(data.montant)) }}
                </template>
            </Column>
            <Column sortable :hidden="hiddenCol.ac">
                <template #header>
                    <span v-tooltip.bottom="'Montant max si accord cadre'" class="p-datatable-column-title" data-pc-section="columntitle">AC</span>
                </template>
                <template #body="{ data }">
                    {{ data.montant_max_accord_cadre ? formatCurrency(parseFloat(data.montant_max_accord_cadre)) : '' }}
                </template>
            </Column>
        </DataTable>
        <BoutonIframe v-if="acheteurUid" :acheteurUid path="marches" name="La liste des marchés publics passés" />
    </section>

    <ModaleMarche v-model="marcheUid" />
</template>
