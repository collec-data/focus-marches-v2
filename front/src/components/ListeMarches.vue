<script setup lang="ts">
import { getListeMarches } from '@/client';
import { exportMarchesCSV, exportMarchesExcel, exportMarchesPdf } from '@/service/ExportDatatableService';
import { formatBoolean, formatCurrency, formatDate, getCatEntreprise, structureName } from '@/service/HelpersService';
import { useStructureIdentifiee } from '@/service/UseStructureIdentifiee';
import { useReactiveFetch } from '@/utils/query';
import { FilterMatchMode } from '@primevue/core/api';
import { computed, ref, watch } from 'vue';

import type { MarcheAllegeDto } from '@/client';
import type { PropType } from 'vue';

// Pas de valeur par défaut : `undefined` signifie « acheteur demandé mais pas encore identifié »,
// tandis que `null` signifie « aucun acheteur demandé », donc aucun filtre.
const props = defineProps({
    acheteurUid: { type: Number as PropType<number | null>, required: false },
    acheteurSiret: { type: String as PropType<string | null>, required: false },
    vendeurUid: { type: Number as PropType<number | null>, required: false },
    dateMin: { type: Date as PropType<Date | null>, required: false },
    dateMax: { type: Date as PropType<Date | null>, required: false }
});

const filters = ref({
    global: { value: null, matchMode: FilterMatchMode.CONTAINS },
    cpv: { value: null, matchMode: FilterMatchMode.EQUALS },
    objet: { value: null, matchMode: FilterMatchMode.IN },
    'acheteur.nom': { value: null, matchMode: FilterMatchMode.IN },
    montant: { value: null, matchMode: FilterMatchMode.EQUALS }
});

const {
    uid,
    erreur: erreurAcheteur,
    refetch: refetchAcheteur
} = useStructureIdentifiee(
    () => props.acheteurUid,
    () => props.acheteurSiret
);

const options = computed(() => {
    if (uid.value === undefined) {
        return undefined;
    }
    return {
        query: {
            date_debut: props.dateMin ?? undefined,
            date_fin: props.dateMax ?? undefined,
            acheteur_uid: uid.value ?? undefined,
            vendeur_uid: props.vendeurUid ?? undefined
        }
    };
});

const { etat, refetch } = useReactiveFetch(getListeMarches, options);

const listeMarches = computed<Array<MarcheAllegeDto>>(() => (etat.value.statut === 'succes' ? etat.value.data : []));

watch([() => props.dateMin, () => props.dateMax, () => props.vendeurUid], () => {
    refetch();
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
        <h2 class="title">Tous les marchés</h2>
        <p>Ce tableau affiche les principales informations des marchés. Cliquez sur «&nbsp;Voir&nbsp;» pour accéder au détail de chaque marché.</p>

        <ErreurChargement v-if="erreurAcheteur" :erreur="erreurAcheteur" message="Aucune structure ne correspond à ce SIRET" @retry="refetchAcheteur" />
        <ChargementEnCours v-else-if="uid === undefined" class="my-4" />
        <ErreurChargement v-else-if="etat.statut === 'erreur'" :erreur="etat.erreur" message="Le chargement des marchés a échoué" class="my-4" @retry="refetch" />

        <DataTable
            v-else
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
            :loading="etat.statut === 'chargement'"
        >
            <template #empty>
                <!-- Le message « aucun marché » n'est vrai qu'une fois la réponse reçue :
                     on ne l'affiche pas pendant le chargement. -->
                <div v-if="etat.statut === 'succes'" class="text-center">
                    <Badge size="xlarge" severity="info">Aucun marché</Badge>
                </div>
            </template>
            <template #header>
                <div class="flex flex-row">
                    <div class="basis-1/2 flex gap-1">
                        <Button icon="pi pi-table" label="CSV" severity="secondary" size="small" @click="exportMarchesCSV(listeMarches)" />
                        <Button icon="pi pi-file-excel" label="Excel" severity="secondary" size="small" @click="exportMarchesExcel(listeMarches, 'Liste des marchés')" />
                        <Button icon="pi pi-file-pdf" label="PDF" severity="secondary" size="small" @click="exportMarchesPdf(listeMarches, 'Liste des marchés')" />
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
        <BoutonIframe v-if="acheteurSiret" :path="'acheteur/' + acheteurSiret + '/marches'" name="La liste des marchés publics passés" />
    </section>

    <ModaleMarche v-model="marcheUid" />
</template>
