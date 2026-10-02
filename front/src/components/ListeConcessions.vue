<script setup lang="ts">
import { type ContratConcessionDto, getListeConcessions } from '@/client';
import { exportConcessionsCSV, exportConcessionsExcel, exportConcessionsPdf } from '@/service/ExportDatatableService';
import { formatCurrency, formatDate, structureName } from '@/service/HelpersService';
import { useStructureIdentifiee } from '@/service/UseStructureIdentifiee';
import { useReactiveFetch } from '@/utils/query';
import { computed, ref, watch } from 'vue';

import type { PropType } from 'vue';

// Pas de valeur par défaut : `undefined` signifie « autorité encore non identifiée », `null` « aucune autorité demandée ».
const props = defineProps({
    autoriteConcedanteUid: { type: Number as PropType<number | null>, required: false },
    autoriteConcedanteSiret: { type: String as PropType<string | null>, required: false },
    concessionnaireUid: { type: Number as PropType<number | null>, required: false },
    dateMin: { type: Date as PropType<Date | null>, required: false },
    dateMax: { type: Date as PropType<Date | null>, required: false }
});

const {
    uid,
    erreur: erreurAcheteur,
    refetch: refetchAcheteur
} = useStructureIdentifiee(
    () => props.autoriteConcedanteUid,
    () => props.autoriteConcedanteSiret
);

const options = computed(() => {
    if (uid.value === undefined) {
        return undefined;
    }
    return {
        query: {
            date_debut: props.dateMin ?? undefined,
            date_fin: props.dateMax ?? undefined,
            autorite_concedante_uid: uid.value === null ? undefined : String(uid.value),
            concessionnaire_uid: props.concessionnaireUid === null || props.concessionnaireUid === undefined ? undefined : String(props.concessionnaireUid)
        }
    };
});

const { etat, refetch } = useReactiveFetch(getListeConcessions, options);

const listeConcessions = computed<Array<ContratConcessionDto>>(() => (etat.value.statut === 'succes' ? etat.value.data : []));

watch([() => props.dateMin, () => props.dateMax, () => props.concessionnaireUid], () => {
    refetch();
});

const concessionUid = ref(null);
</script>

<template>
    <section>
        <h2>Contrat-concessions</h2>

        <ErreurChargement v-if="erreurAcheteur" :erreur="erreurAcheteur" message="Aucune structure ne correspond à ce SIRET" @retry="refetchAcheteur" />
        <ChargementEnCours v-else-if="uid === undefined" class="my-4" />
        <ErreurChargement v-else-if="etat.statut === 'erreur'" :erreur="etat.erreur" message="Le chargement des concessions a échoué" class="my-4" @retry="refetch" />

        <DataTable
            v-else
            :value="listeConcessions"
            sortField="date_notification"
            :sortOrder="-1"
            size="small"
            stripedRows
            :pt="{ column: { headerCell: { style: 'font-size:0.8rem; text-transform:uppercase;' } } }"
            :loading="etat.statut === 'chargement'"
        >
            <template #empty>
                <div v-if="etat.statut === 'succes'" class="text-center">
                    <Badge size="xlarge" severity="info">Aucune concession</Badge>
                </div>
            </template>
            <template #header>
                <div class="flex flex-row">
                    <div class="basis-1/2 flex gap-1">
                        <Button icon="pi pi-table" label="CSV" severity="secondary" size="small" @click="exportConcessionsCSV(listeConcessions)" />
                        <Button icon="pi pi-file-excel" label="Excel" severity="secondary" size="small" @click="exportConcessionsExcel(listeConcessions)" />
                        <Button icon="pi pi-file-pdf" label="PDF" severity="secondary" size="small" @click="exportConcessionsPdf(listeConcessions, 'Liste des concessions')" />
                    </div>
                </div>
            </template>
            <Column header="Détails">
                <template #body="{ data }"> <Button label="Voir" aria-label="Voir les détails de la concessions" @click="concessionUid = data.uid" /> </template
            ></Column>
            <Column v-if="uid === null" field="autorite_concedante.nom" header="Autorité" sortable>
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
        <BoutonIframe v-if="autoriteConcedanteSiret" :path="'acheteur/' + autoriteConcedanteSiret + '/concessions'" name="La liste des concession passées" />
    </section>
    <ModaleConcession v-model="concessionUid" />
</template>
