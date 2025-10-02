<script setup lang="ts">
import type { MarcheAllegeDto } from '@/client';
import { getListeMarchesMarcheGet } from '@/client';
import { formatBoolean, formatCurrency, formatDate } from '@/service/HelpersService';
import { FilterMatchMode } from '@primevue/core/api';
import { onMounted, ref } from 'vue';

const props = defineProps({
    acheteurUid: { type: [String, null], default: null },
    vendeurUid: { type: [String, null], default: null }
});

const filters = ref({
    global: { value: null, matchMode: FilterMatchMode.CONTAINS },
    cpv: { value: null, matchMode: FilterMatchMode.EQUALS },
    objet: { value: null, matchMode: FilterMatchMode.IN },
    'acheteur.nom': { value: null, matchMode: FilterMatchMode.IN },
    montant: { value: null, matchMode: FilterMatchMode.EQUALS }
});

const listeMarches = ref<Array<MarcheAllegeDto>>([]);

onMounted(() => {
    getListeMarchesMarcheGet({
        query: {
            acheteur_uid: props.acheteurUid,
            vendeur_uid: props.vendeurUid
        }
    }).then((response) => {
        if (response.data) {
            listeMarches.value = response.data;
        }
    });
});

const countSousTraitants = (value: Array<any>) => {
    return value.length ? value.length : '';
};
</script>

<template>
    <section>
        <h2 class="title">Tous les marchés de ...</h2>
        <p>Ce tableau affiche les principales informations des marchés de ... . Cliquez sur "Voir" pour accéder au détail de chaque marché.</p>
        <DataTable v-model:filters="filters" :value="listeMarches" sortField="date_notification" :sortOrder="-1" stripedRows paginator :rows="10" :rowsPerPageOptions="[10, 25, 50]">
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
            <Column header="Détails" sortable>
                <template #body=""> <Button label="Voir" aria-label="Voir" disabled /> </template
            ></Column>
            <Column field="cpv" header="CPV" sortable></Column>
            <Column field="objet" header="Objet" sortable></Column>
            <Column v-if="acheteurUid == null" field="acheteur.nom" header="Acheteur" sortable></Column>
            <Column field="" header="Fournisseur" sortable></Column>
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
            <Column field="" header="Considérations environnementales" sortable></Column>
            <Column field="" header="Considérations sociales" sortable></Column>
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
    </section>
</template>
