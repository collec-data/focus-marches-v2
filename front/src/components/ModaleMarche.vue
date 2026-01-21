<script setup lang="ts">
import { computed, ref, watchEffect } from 'vue';

import { getListeMarches, getMarche, ModaliteExecution, TechniqueAchat, type MarcheAllegeDto, type MarcheDto } from '@/client';
import { getNomDepartement } from '@/service/Departements';
import { formatBoolean, formatCurrency, formatDate, getCatEntreprise, structureName } from '@/service/HelpersService';

const marcheUid = defineModel<number | null>();

const marcheDetaille = ref<Partial<MarcheDto>>();
const showModale = computed(() => marcheDetaille.value != null);
const marchesSubsequents = ref<Partial<MarcheAllegeDto[]>>([]);

watchEffect(() => {
    if (marcheUid.value) {
        getMarche({ path: { uid: marcheUid.value } }).then((response) => {
            if (response.data) {
                marcheDetaille.value = response.data;
                if (response.data.techniques_achat?.includes(TechniqueAchat.ACCORD_CADRE) && response.data.modalites_execution?.includes(ModaliteExecution.MARCHÉS_SUBSÉQUENTS)) {
                    getListeMarches({ query: { accord_cadre_uid: response.data.uid } }).then((response) => {
                        if (response.data) {
                            marchesSubsequents.value = response.data;
                        }
                    });
                }
            }
        });
    }
});

function hideMarcheModal() {
    marcheUid.value = null;
    marcheDetaille.value = undefined;
    marchesSubsequents.value = [];
}
</script>

<template>
    <Dialog :visible="showModale" modal :header="'Détails du contrat ' + marcheDetaille?.id" class="max-w-full" @update:visible="hideMarcheModal">
        <div class="flex flex-row flex-wrap">
            <div class="bg-neutral-200 basis-10rem pl-3 pr-3">
                <div class="key">Montant</div>
                <div class="value text-xl">
                    {{ marcheDetaille?.montant ? formatCurrency(parseFloat(marcheDetaille.montant)) : '' }}
                    <i v-if="marcheDetaille?.montant_initial && marcheDetaille?.montant != marcheDetaille?.montant_initial" v-tooltip="'Montant initial : ' + formatCurrency(parseFloat(marcheDetaille?.montant_initial))" class="pi pi-history ml-2"></i>
                </div>

                <div class="key">Durée</div>
                <div class="value">
                    {{ marcheDetaille?.duree_mois }} mois
                    <i v-if="marcheDetaille?.duree_mois_initiale && marcheDetaille?.duree_mois != marcheDetaille?.duree_mois_initiale" v-tooltip.bottom="'Durée initiale : ' + marcheDetaille?.duree_mois_initiale" class="pi pi-history ml-2"></i>
                </div>

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
                    <img src="@/assets/images/flag-fr.svg" alt="le drapeau français" class="flag" /> {{ marcheDetaille?.origine_france }}% | <img src="@/assets/images/flag-eu.svg" alt="le drapeau européen" class="flag" />
                    {{ marcheDetaille?.origine_ue }}%
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
                    <div class="value">{{ marcheDetaille?.cpv?.code + ' ' + marcheDetaille?.cpv?.libelle }}</div>
                </div>
                <hr />
                <div>
                    <div class="key">Objet</div>
                    <p>{{ marcheDetaille?.objet }}</p>
                </div>
                <div v-if="marcheDetaille?.techniques_achat?.includes(TechniqueAchat.ACCORD_CADRE) && marcheDetaille.modalites_execution?.includes(ModaliteExecution.MARCHÉS_SUBSÉQUENTS)">
                    <hr />
                    <div class="key">Accord-cadre</div>
                    <DataTable :value="marchesSubsequents">
                        <template #empty>
                            <div class="text-center">
                                <Badge size="xlarge" severity="info">Aucun marché subséquent</Badge>
                            </div>
                        </template>
                        <Column field="objet" header="Objet"></Column>
                        <Column field="cpv" header="CPV"></Column>
                        <Column field="acheteur.nom" header="Acheteur">
                            <template #body="{ data }">{{ structureName(data.acheteur) }}</template>
                        </Column>
                        <Column field="sous_traitant.nom" header="Fournisseur">
                            <template #body="{ data }">
                                <div v-for="titulaire in data.titulaires" :key="titulaire.uid">
                                    {{ structureName(titulaire) }}&nbsp;<span v-tooltip="getCatEntreprise(titulaire.cat_entreprise)" class="text-sm">[{{ titulaire.cat_entreprise }}]</span>
                                </div>
                            </template>
                        </Column>
                        <Column field="date_notification" header="Date de notif">
                            <template #body="{ data }">{{ formatDate(data.date_notification) }}</template>
                        </Column>
                        <Column field="montant" header="Montant">
                            <template #body="{ data }">
                                {{ formatCurrency(parseFloat(data.montant)) }}
                            </template>
                        </Column>
                    </DataTable>
                </div>
                <div v-if="marcheDetaille?.sous_traitance_declaree || marcheDetaille?.actes_sous_traitance?.length">
                    <hr />
                    <div class="key">Sous-traitance</div>
                    <DataTable :value="marcheDetaille.actes_sous_traitance">
                        <template #empty>
                            <div class="text-center">
                                <Badge size="xlarge" severity="info">Pas d'actes de sous-traitance</Badge>
                            </div>
                        </template>
                        <Column field="sous_traitant.nom" header="Fournisseur">
                            <template #body="{ data }">
                                <RouterLink :to="'/fournisseur/' + data.uid">
                                    <Button icon="pi pi-fw pi-link" aria-label="Voir la page du fournisseur" severity="secondary" size="small"></Button>
                                    {{ structureName(data.sous_traitant) }}
                                </RouterLink>
                            </template>
                        </Column>
                        <Column field="" header="Cat. entreprise">
                            <template #body="{ data }">{{ getCatEntreprise(data.sous_traitant.cat_entreprise) }}</template>
                        </Column>
                        <Column field="acheteur.nom" header="Acheteur" sortable>
                            <template #body="{ data }">{{ structureName(data.acheteur) }}</template>
                        </Column>
                        <Column field="date_notification" header="Date de notif">
                            <template #body="{ data }">{{ formatDate(data.date_notification) }}</template>
                        </Column>
                        <Column field="montant" header="Montant">
                            <template #body="{ data }">
                                {{ formatCurrency(parseFloat(data.montant)) }}
                            </template>
                        </Column>
                        <Column header="Part montant total">
                            <template #body="{ data }"> {{ marcheDetaille?.montant ? ((data.montant * 100) / parseFloat(marcheDetaille.montant)).toFixed(2) : '' }}% </template>
                        </Column>
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

.flag {
    display: inline-block;
    width: 1.2rem;
    border-radius: 20%;
}
</style>
