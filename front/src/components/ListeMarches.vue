<script setup lang="ts">
import { getListeMarchesMarcheGet, getMarcheMarcheUidGet } from '@/client';
import { getNomDepartement } from '@/service/Departements';
import { formatBoolean, formatCurrency, formatDate } from '@/service/HelpersService';
import { FilterMatchMode } from '@primevue/core/api';
import { computed, onMounted, ref, watch } from 'vue';

import type { MarcheAllegeDtoOutput, MarcheDto } from '@/client';

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

const marcheDetaille = ref<Partial<MarcheDto>>();
const showModale = computed(() => marcheDetaille.value != null);

function openMarcheModal(uid: number) {
    getMarcheMarcheUidGet({ path: { uid: uid } }).then((response) => {
        if (response.data) {
            marcheDetaille.value = response.data;
        }
    });
}

function hideMarcheModal() {
    marcheDetaille.value = undefined;
}
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
                <template #body="{ data }"> <Button label="Voir" aria-label="Voir les détails du marché" @click="openMarcheModal(data.uid)" /> </template
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

    <Dialog :visible="showModale" modal :header="'Détails du contrat ' + marcheDetaille?.id" class="max-w-full" @update:visible="hideMarcheModal">
        <div class="flex flex-row flex-wrap">
            <div class="bg-neutral-200 basis-10rem pl-3 pr-3">
                <div class="key">Montant</div>
                <div class="value text-xl">{{ marcheDetaille?.montant ? formatCurrency(parseFloat(marcheDetaille.montant)) : '' }}</div>

                <div class="key">Durée</div>
                <div class="value">{{ marcheDetaille?.duree_mois }} mois</div>

                <div class="key">Lieu d'éxécution</div>
                <div class="value">
                    {{ marcheDetaille?.lieu?.type_code == 'Code département' ? getNomDepartement(marcheDetaille.lieu.code) + ' (' + marcheDetaille.lieu.code + ')' : marcheDetaille?.lieu?.type_code + ' - ' + marcheDetaille?.lieu?.code }}
                </div>

                <div class="key">Date de notification</div>
                <div class="value">{{ marcheDetaille?.date_notification ? formatDate(marcheDetaille.date_notification) : '' }}</div>

                <div class="key">Type de marché</div>
                <div class="value">{{ marcheDetaille?.nature }}</div>

                <div class="key">Procédure</div>
                <div class="value">{{ marcheDetaille?.procedure }}</div>

                <div class="key">Forme de prix</div>
                <div class="value">{{ marcheDetaille?.forme_prix }}</div>

                <div class="key">Marché innovant</div>
                <div class="value">{{ marcheDetaille?.marche_innovant ? formatBoolean(marcheDetaille?.marche_innovant) : '' }}</div>

                <div class="key">Nombre d'offres reçues</div>
                <div class="value">{{ marcheDetaille?.offres_recues }}</div>

                <div class="key">Part de produits issus ou fabriqués</div>
                <div class="value" aria-label="Pourcentage d'origine France et pourcentage d'origine de l'Union Européenne">
                    <span class="fi fi-fr"></span> {{ marcheDetaille?.origine_france }}% | <span class="fi fi-eu"></span> {{ marcheDetaille?.origine_ue }}%
                </div>

                <div class="key">Considération environnementale</div>
                <div class="value">{{ marcheDetaille?.considerations_environnementales ? marcheDetaille.considerations_environnementales.join(', ') : '' }}</div>

                <div class="key">Considération sociale</div>
                <div class="value">{{ marcheDetaille?.considerations_sociales ? marcheDetaille.considerations_sociales.join(', ') : '' }}</div>
            </div>
            <div class="basis-auto p-3 shrink-0.5 max-w-3xl">
                <div class="flex flex-row flex-wrap">
                    <div class="basis-1/2">
                        <div class="key">Acheteur</div>
                        <div>{{ marcheDetaille?.acheteur?.nom }}</div>
                        <div class="text-sm">{{ marcheDetaille?.acheteur?.type_identifiant }} - {{ marcheDetaille?.acheteur?.identifiant }}</div>
                        <RouterLink v-if="marcheDetaille?.acheteur" :to="'/acheteur/' + marcheDetaille.acheteur.uid">
                            <Button icon="pi pi-fw pi-link" label="Page de l'acheteur" aria-label="Voir la page de l'acheteur" severity="secondary" size="small"></Button>
                        </RouterLink>
                    </div>
                    <div class="basis-1/2">
                        <div class="key">Titulaire</div>
                        <div v-for="titulaire in marcheDetaille?.titulaires" :key="titulaire.uid">
                            <div>{{ titulaire.nom }}</div>
                            <div class="text-sm">{{ titulaire.type_identifiant }} - {{ titulaire.identifiant }}</div>
                            <RouterLink :to="'/fournisseur/' + titulaire.uid">
                                <Button icon="pi pi-fw pi-link" label="Page du titulaire" aria-label="Voir la page du titulaire" severity="secondary" size="small"></Button>
                            </RouterLink>
                        </div>
                    </div>
                </div>
                <hr />
                <div class="mt-5">
                    <div class="key">Code CPV</div>
                    <div class="value">{{ marcheDetaille?.cpv }}</div>
                </div>
                <hr />
                <div>
                    <div class="key">Objet</div>
                    <p>{{ marcheDetaille?.objet }}</p>
                </div>
                <div v-if="marcheDetaille?.accord_cadre">
                    <hr />
                    <div class="key">Accord-cadre</div>
                </div>
                <div v-if="marcheDetaille?.sous_traitance_declaree">
                    <hr />
                    <div class="key">Sous-traitance</div>
                    <DataTable :value="marcheDetaille.actes_sous_traitance">
                        <Column field="sous_traitant.nom" header="Fournisseur">
                            <template #body="{ data }">
                                <RouterLink :to="'/fournisseur/' + data.uid">
                                    <Button icon="pi pi-fw pi-link" aria-label="Voir la page du fournisseur" severity="secondary" size="small"></Button>
                                    {{ data.sous_traitant.nom ? data.sous_traitant.nom : data.sous_traitant.type_identifiant + ' ' + data.sous_traitant.identifiant }}
                                </RouterLink>
                            </template>
                        </Column>
                        <Column field="" header="Cat. entreprise"></Column>
                        <Column field="date_notification" header="Date de notif">
                            <template #body="{ data }">{{ formatDate(data.date_notification) }}</template>
                        </Column>
                        <Column field="montant" header="Montant">
                            <template #body="{ data }">
                                {{ formatCurrency(parseFloat(data.montant)) }}
                            </template>
                        </Column>
                        <Column header="Part montant total">
                            <template #body="{ data }"> {{ marcheDetaille?.montant ? ((data.montant * 100) / parseFloat(marcheDetaille.montant)).toFixed(2) : '' }}% </template></Column
                        >
                    </DataTable>
                </div>
            </div>
        </div>
    </Dialog>
</template>

<style scoped>
.key {
    text-transform: uppercase;
    font-size: 0.8rem;
    margin-bottom: 0.2rem;
    margin-top: 1rem;
}

.value {
    margin-bottom: 1rem;
}
</style>
