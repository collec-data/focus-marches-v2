<script setup lang="ts">
import { type ContratConcessionDto, getListeConcessionsContratConcessionGet } from '@/client';
import { formatCurrency, formatDate, structureName } from '@/service/HelpersService';
import { onMounted, ref, watch } from 'vue';

const props = defineProps({
    autoriteConcedanteUid: { type: [String, null], default: null },
    concessionnaireUid: { type: [String, null], default: null },
    dateMin: { type: [Date, null], default: null },
    dateMax: { type: [Date, null], default: null }
});

const listeConcessions = ref<Array<ContratConcessionDto>>([]);

function fetchData() {
    getListeConcessionsContratConcessionGet({
        query: {
            date_debut: props.dateMin,
            date_fin: props.dateMax,
            autorite_concedante_uid: props.autoriteConcedanteUid,
            concessionnaire_uid: props.concessionnaireUid
        }
    }).then((response) => {
        if (response.data) {
            listeConcessions.value = response.data;
        }
    });
}

onMounted(() => {
    fetchData();
});

watch([() => props.dateMin, () => props.dateMax, () => props.autoriteConcedanteUid, () => props.concessionnaireUid], () => {
    fetchData();
});

const concessionUid = ref(null);
</script>

<template>
    <section>
        <h2>Contrat-concessions</h2>
        <DataTable :value="listeConcessions" sortField="date_notification" :sortOrder="-1" size="small" stripedRows :pt="{ column: { headerCell: { style: 'font-size:0.8rem; text-transform:uppercase;' } } }">
            <Column header="Détails">
                <template #body="{ data }"> <Button label="Voir" aria-label="Voir les détails de la concessions" @click="concessionUid = data.uid" /> </template
            ></Column>
            <Column v-if="!autoriteConcedanteUid" field="autorite_concedante.nom" header="Autorité" sortable>
                <template #body="{ data }">{{ structureName(data.autorite_concedante) }}</template>
            </Column>
            <Column header="Concessionnaires">
                <template #body="{ data }">
                    <div v-for="concessionnaire in data.concessionnaires" :key="concessionnaire.uid">{{ structureName(concessionnaire) }}</div>
                </template>
            </Column>
            <Column field="objet" header="Objet" sortable style="min-width: 20rem"></Column>
            <Column field="date_publication" header="Date de publication" sortable>
                <template #body="{ data }">
                    {{ formatDate(data.date_publication) }}
                </template>
            </Column>
            <Column field="valeur_globale" header="Valeur Globale" dataType="numeric" sortable>
                <template #body="{ data }">
                    {{ formatCurrency(parseFloat(data.valeur_globale)) }}
                </template>
            </Column>
        </DataTable>
    </section>
    <ModaleConcession :concessionUid />
</template>
