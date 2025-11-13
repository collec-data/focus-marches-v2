<script setup lang="ts">
import { type ContratConcessionDto, getConcessionContratConcessionUidGet } from '@/client';
import { formatCurrency, formatDate } from '@/service/HelpersService';
import { computed, ref, watch } from 'vue';

const props = defineProps({ concessionUid: { type: [Number, null], default: null } });

const concession = ref<Partial<ContratConcessionDto>>();
const showModale = computed(() => concession.value != null);

watch(
    () => props.concessionUid,
    () => {
        if (props.concessionUid) {
            getConcessionContratConcessionUidGet({ path: { uid: props.concessionUid } }).then((response) => {
                if (response.data) {
                    concession.value = response.data;
                }
            });
        }
    }
);

function hideConcessionModal() {
    concession.value = undefined;
}
</script>

<template>
    <Dialog :visible="showModale" modal :header="'Détails du contrat ' + concession?.id" class="max-w-full" @update:visible="hideConcessionModal">
        <div class="flex flex-row flex-wrap">
            <div class="bg-neutral-200 basis-10rem pl-3 pr-3">
                <div class="key">Montant</div>
                <div class="value text-xl">
                    {{ concession?.valeur_globale ? formatCurrency(parseFloat(concession.valeur_globale)) : '' }}
                    <i
                        v-if="concession?.valeur_globale_initiale && concession?.valeur_globale != concession?.valeur_globale_initiale"
                        v-tooltip="'valeur_globale initial : ' + formatCurrency(parseFloat(concession?.valeur_globale_initiale))"
                        class="pi pi-history ml-2"
                    ></i>
                </div>

                <div class="key">Dont subventions publiques</div>
                <div class="value">{{ concession?.montant_subvention_publique ? formatCurrency(parseFloat(concession.montant_subvention_publique)) : '' }}</div>

                <div class="key">Durée</div>
                <div class="value">
                    {{ concession?.duree_mois }} mois
                    <i v-if="concession?.duree_mois_initiale && concession?.duree_mois != concession?.duree_mois_initiale" v-tooltip.bottom="'Durée initiale : ' + concession?.duree_mois_initiale" class="pi pi-history ml-2"></i>
                </div>

                <div class="key">Type de marché</div>
                <div class="value">{{ concession?.nature }}</div>

                <div class="key">Procédure</div>
                <div class="value">{{ concession?.procedure }}</div>

                <div class="key">Date de signature</div>
                <div class="value">{{ concession?.date_signature ? formatDate(concession.date_signature) : '' }}</div>

                <div class="key">Date de début d'exécution</div>
                <div class="value">{{ concession?.date_debut_execution ? formatDate(concession.date_debut_execution) : '' }}</div>

                <div class="key">Considération environnementale</div>
                <div class="value">{{ concession?.considerations_environnementales ? concession.considerations_environnementales.join(', ') : '' }}</div>

                <div class="key">Considération sociale</div>
                <div class="value">{{ concession?.considerations_sociales ? concession.considerations_sociales.join(', ') : '' }}</div>
            </div>
            <div class="basis-auto p-3 shrink-0.5 max-w-3xl">
                <div class="flex flex-row flex-wrap">
                    <div class="basis-1/2">
                        <div class="key">Autorité concédante</div>
                        <div>{{ concession?.autorite_concedante?.nom }}</div>
                        <div class="text-sm">{{ concession?.autorite_concedante?.type_identifiant }} - {{ concession?.autorite_concedante?.identifiant }}</div>
                        <RouterLink v-if="concession?.autorite_concedante" :to="'/acheteur/' + concession.autorite_concedante.uid">
                            <Button icon="pi pi-fw pi-link" label="Page de l'autorité concédante" aria-label="Voir la page de l'autorité concédante" severity="secondary" size="small"></Button>
                        </RouterLink>
                    </div>
                    <div class="basis-1/2">
                        <div class="key">Concessionnaires</div>
                        <div v-for="concessionnaire in concession?.concessionnaires" :key="concessionnaire.uid">
                            <div>{{ concessionnaire.nom }}</div>
                            <div class="text-sm">{{ concessionnaire.type_identifiant }} - {{ concessionnaire.identifiant }}</div>
                            <RouterLink :to="'/fournisseur/' + concessionnaire.uid">
                                <Button icon="pi pi-fw pi-link" label="Page du concessionnaire" aria-label="Voir la page du concessionnaire" severity="secondary" size="small"></Button>
                            </RouterLink>
                        </div>
                    </div>
                </div>
                <hr />
                <div>
                    <div class="key">Objet</div>
                    <p>{{ concession?.objet }}</p>
                </div>
                <hr />
                <div v-if="concession?.donnees_execution?.length" class="key">Données d'exécution</div>
                <DataTable v-if="concession?.donnees_execution?.length" :value="concession?.donnees_execution">
                    <Column field="date_publication" header="Date de publication">
                        <template #body="{ data }">{{ formatDate(data.date_publication) }}</template>
                    </Column>
                    <Column field="depenses_investissement" header="Investissement">
                        <template #body="{ data }">
                            {{ formatCurrency(parseFloat(data.depenses_investissement)) }}
                        </template>
                    </Column>
                    <Column header="Tarifs">
                        <template #body="{ data }">
                            <div v-for="tarif in data.tarifs" :key="tarif.uid">
                                <span>{{ tarif.intitule }}</span> : <span>{{ formatCurrency(tarif.tarif) }}</span>
                            </div>
                        </template>
                    </Column>
                </DataTable>
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
