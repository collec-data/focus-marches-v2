<script setup lang="ts">
import { computed } from 'vue';

import { getListeMarches, getMarche, ModaliteExecution, TechniqueAchat } from '@/client';
import { getNomDepartement } from '@/service/Departements';
import { formatBoolean, formatCurrency, formatDate, getCatEntreprise, structureName } from '@/service/HelpersService';
import { useReactiveFetch } from '@/utils/query';

const marcheUid = defineModel<number | null>();

const marcheOptions = computed(() => (marcheUid.value ? { path: { uid: marcheUid.value } } : undefined));

const { etat: etatMarche, refetch: refetchMarche } = useReactiveFetch(getMarche, marcheOptions);

const marche = computed(() => (etatMarche.value.statut === 'succes' ? etatMarche.value.data : null));

/** La modale suit la demande d'ouverture, pas la donnée reçue : elle s'affiche et charge. */
const showModale = computed(() => marcheUid.value != null);

/** Les marchés subséquents n'existent que pour un accord-cadre Executé en marché subséquent. */
const aDesMarchesSubsequents = computed(() => Boolean(marche.value?.techniques_achat?.includes(TechniqueAchat.ACCORD_CADRE) && marche.value?.modalites_execution?.includes(ModaliteExecution.MARCHÉS_SUBSÉQUENTS)));

const subsequentsOptions = computed(() => (aDesMarchesSubsequents.value ? { query: { accord_cadre_uid: marche.value!.uid } } : undefined));

const { etat: etatSubsequents } = useReactiveFetch(getListeMarches, subsequentsOptions);

const marchesSubsequents = computed(() => (etatSubsequents.value.statut === 'succes' ? etatSubsequents.value.data : []));

function hideMarcheModal() {
    marcheUid.value = null;
}

function considerationsEnvironnementalesEtSociales(list: string[] | undefined): string {
    if (list == null) {
        return 'Aucune'; // Absence de valeur
    }
    if (list.length) {
        return list.join(', ');
    }
    return 'Non renseigné'; // liste présente mais vide
}
</script>

<template>
    <Dialog :visible="showModale" modal :header="'Détails du contrat ' + marche?.id" class="max-w-full" @update:visible="hideMarcheModal">
        <ErreurChargement v-if="etatMarche.statut === 'erreur'" :erreur="etatMarche.erreur" message="Le détail du marché n'a pas pu être chargé" @retry="refetchMarche" />
        <ChargementEnCours v-else-if="!marche" libelle="Chargement du marché" />
        <div v-else class="flex flex-row flex-wrap">
            <div class="bg-neutral-200 basis-10rem pl-3 pr-3">
                <div class="key">Montant</div>
                <div class="value text-xl">
                    {{ marche?.montant ? formatCurrency(parseFloat(marche.montant)) : '' }}
                    <i v-if="marche?.montant_initial && marche?.montant != marche?.montant_initial" v-tooltip="'Montant initial : ' + formatCurrency(parseFloat(marche?.montant_initial))" class="pi pi-history ml-2"></i>
                </div>

                <div class="key">Durée</div>
                <div class="value">
                    {{ marche?.duree_mois }} mois
                    <i v-if="marche?.duree_mois_initiale && marche?.duree_mois != marche?.duree_mois_initiale" v-tooltip.bottom="'Durée initiale : ' + marche?.duree_mois_initiale" class="pi pi-history ml-2"></i>
                </div>

                <div class="key">Lieu d'éxécution</div>
                <div class="value">
                    {{ marche?.lieu?.type_code == 'Code département' ? getNomDepartement(marche.lieu.code) + ' (' + marche.lieu.code + ')' : marche?.lieu?.type_code + ' - ' + marche?.lieu?.code }}
                </div>

                <div class="key">Date de notification</div>
                <div class="value">{{ marche?.date_notification ? formatDate(marche.date_notification) : '' }}</div>

                <div class="key">Type de marché</div>
                <div class="value">{{ marche?.nature }}</div>

                <div class="key">Procédure</div>
                <div class="value">{{ marche?.procedure }}</div>

                <div class="key">Forme de prix</div>
                <div class="value">{{ marche?.forme_prix }}</div>

                <div class="key">Marché innovant</div>
                <div class="value">{{ marche?.marche_innovant ? formatBoolean(marche?.marche_innovant) : '' }}</div>

                <div class="key">Nombre d'offres reçues</div>
                <div class="value">{{ marche?.offres_recues }}</div>

                <div class="key">Part de produits issus ou fabriqués</div>
                <div class="value">
                    <template v-if="marche?.origine_france == null && marche?.origine_ue == null">Non renseigné</template>
                    <template v-else>
                        <template v-if="marche?.origine_france != null"><img src="@/assets/images/flag-fr.svg" alt="" class="flag" /> {{ marche?.origine_france }}% <span class="sr-only">en France</span></template>
                        <template v-if="marche?.origine_france != null && marche?.origine_ue != null"> | </template>
                        <template v-if="marche?.origine_ue != null"><img src="@/assets/images/flag-eu.svg" alt="" class="flag" /> {{ marche?.origine_ue }}% <span class="sr-only">dans l'Union Européenne</span></template>
                    </template>
                </div>

                <div class="key">Considération environnementale</div>
                <div class="value">{{ considerationsEnvironnementalesEtSociales(marche?.considerations_environnementales) }}</div>

                <div class="key">Considération sociale</div>
                <div class="value">{{ considerationsEnvironnementalesEtSociales(marche?.considerations_sociales) }}</div>
            </div>
            <div class="basis-auto p-3 shrink-0.5 max-w-3xl">
                <div class="flex flex-row flex-wrap">
                    <div class="basis-1/2">
                        <div class="key">Acheteur</div>
                        <div>{{ marche?.acheteur?.nom }}</div>
                        <div class="text-sm">{{ marche?.acheteur?.type_identifiant }} - {{ marche?.acheteur?.identifiant }}</div>
                        <RouterLink v-if="marche?.acheteur" :to="'/acheteur/' + marche.acheteur.uid">
                            <Button icon="pi pi-fw pi-link" label="Page de l'acheteur" aria-label="Voir la page de l'acheteur" severity="secondary" size="small"></Button>
                        </RouterLink>
                    </div>
                    <div class="basis-1/2">
                        <div class="key">Titulaire</div>
                        <div v-for="titulaire in marche?.titulaires" :key="titulaire.uid">
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
                    <div class="value">{{ marche?.cpv?.code + ' ' + marche?.cpv?.libelle }}</div>
                </div>
                <hr />
                <div>
                    <div class="key">Objet</div>
                    <p>{{ marche?.objet }}</p>
                </div>
                <div v-if="marche?.techniques_achat?.includes(TechniqueAchat.ACCORD_CADRE) && marche.modalites_execution?.includes(ModaliteExecution.MARCHÉS_SUBSÉQUENTS)">
                    <hr />
                    <div class="key">Accord-cadre</div>
                    <ErreurChargement v-if="etatSubsequents.statut === 'erreur'" :erreur="etatSubsequents.erreur" message="Le chargement des marchés subséquents a échoué" />
                    <DataTable :value="marchesSubsequents" :loading="etatSubsequents.statut === 'chargement'">
                        <template v-if="etatSubsequents.statut === 'succes'" #empty>
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
                <div v-if="marche?.sous_traitance_declaree || marche?.actes_sous_traitance?.length">
                    <hr />
                    <div class="key">Sous-traitance</div>
                    <DataTable :value="marche.actes_sous_traitance">
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
                            <template #body="{ data }"> {{ marche?.montant ? ((data.montant * 100) / parseFloat(marche.montant)).toFixed(2) : '' }}% </template>
                        </Column>
                    </DataTable>
                </div>
            </div>
        </div>
    </Dialog>
</template>

<style scoped>
.key {
    font-size: 1rem;
    font-weight: 700;
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
