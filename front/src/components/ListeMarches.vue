<script setup lang="ts">
import { getListeMarchesMarcheGet } from '@/client';
import { formatBoolean, formatCurrency, formatDate } from '@/service/HelpersService';
import { FilterMatchMode } from '@primevue/core/api';
import { onMounted, ref, watch } from 'vue';

import type { MarcheAllegeDtoOutput } from '@/client';

const props = defineProps({
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

const listeMarches = ref<Array<MarcheAllegeDtoOutput>>([]);

function fetchData() {
    getListeMarchesMarcheGet({
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
</script>

<template>
    <section>
        <h2 class="title">Tous les marchés de ...</h2>
        <p>Ce tableau affiche les principales informations des marchés de ... . Cliquez sur "Voir" pour accéder au détail de chaque marché.</p>
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
            </template>
            <Column header="Détails">
                <template #body="{ data }"> <Button label="Voir" aria-label="Voir les détails du marché" @click="marcheUid = data.uid" /> </template
            ></Column>
            <Column field="cpv" header="CPV" sortable></Column>
            <Column field="objet" header="Objet" sortable style="min-width: 20rem"></Column>
            <Column v-if="acheteurUid == null" field="acheteur.nom" header="Acheteur" sortable></Column>
            <Column header="Fournisseur">
                <template #body="{ data }">
                    <div v-for="titulaire in data.titulaires" :key="titulaire.uid">{{ titulaire.nom ? titulaire.nom : titulaire.type_identifiant + ' ' + titulaire.identifiant }}</div>
                </template>
            </Column>
            <Column field="" header="Cat entreprise" sortable></Column>
            <Column field="sous_traitance_declaree" header="Sous-traitance" sortable>
                <template #body="{ data }">
                    {{ formatBoolean(data.sous_traitance_declaree) }}
                </template>
            </Column>
            <Column field="actes_sous_traitance" header="Nb sous-traitants" sortable>
                <template #body="{ data }">
                    {{ countSousTraitants(data.actes_sous_traitance) }}
                </template></Column
            >
            <Column field="considerations_environnementales" header="Considérations environnement" sortable>
                <template #body="{ data }">
                    {{ formatBoolean(data.considerations_environnementales?.length > 0) }}
                </template>
            </Column>
            <Column field="considerations_sociales" header="Considérations sociales" sortable>
                <template #body="{ data }">
                    {{ formatBoolean(data.considerations_sociales?.length > 0) }}
                </template>
            </Column>
            <Column field="date_notification" header="Date de notification" sortable>
                <template #body="{ data }">
                    {{ formatDate(data.date_notification) }}
                </template></Column
            >
            <Column field="montant" header="Montant" dataType="numeric" sortable>
                <template #body="{ data }">
                    {{ formatCurrency(parseFloat(data.montant)) }}
                </template>
                ></Column
            >
            <Column field="" header="Montant max si accord cadre" sortable></Column>
        </DataTable>
        <BoutonIframe v-if="acheteurUid" :acheteurUid path="marches" name="La liste des marchés publics passés" />
    </section>

    <ModaleMarche :marcheUid />
</template>
