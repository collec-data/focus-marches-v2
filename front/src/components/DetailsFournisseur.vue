<script setup lang="ts">
import { type StructureEtendueDto } from '@/client';
import { formatCurrency, formatDate, formatNumber, getCatEntreprise, structureName } from '@/service/HelpersService';
import { ref, watchEffect } from 'vue';

import type { PropType } from 'vue';

const props = defineProps({
    vendeur: { type: Object as PropType<Partial<StructureEtendueDto>>, default: () => ({}) }
});

const vendeur = ref<Partial<StructureEtendueDto>>(props.vendeur);
watchEffect(() => {
    vendeur.value = props.vendeur;
});
</script>

<template>
    <section class="mb-10">
        <h2>Localisation et contexte</h2>

        <div class="grid grid-cols-12 gap-5">
            <LeafletMap :lon="vendeur.longitude" :lat="vendeur.latitude" :label="structureName(vendeur) + '<br>' + vendeur.adresse" class="col-span-12 xl:col-span-6" />
            <div class="col-span-12 xl:col-span-6">
                <Tabs value="etablissement">
                    <TabList>
                        <Tab value="etablissement"><i class="pi pi-building"></i> L'établissement</Tab>
                        <Tab value="siege"><i class="pi pi-users"></i> Le siège</Tab>
                        <Tab value="infogreffe"><i class="pi pi-chart-line"></i> Infogreffe</Tab>
                    </TabList>
                    <TabPanels>
                        <TabPanel value="etablissement">
                            <table class="w-full">
                                <tbody>
                                    <tr>
                                        <th>{{ vendeur.type_identifiant ? vendeur.type_identifiant : "Pas de type d'identifiant renseigné" }}</th>
                                        <td>{{ vendeur.identifiant }}</td>
                                    </tr>
                                    <tr>
                                        <th>Date création</th>
                                        <td>{{ vendeur.date_creation ? formatDate(vendeur.date_creation) : '' }}</td>
                                    </tr>
                                    <tr>
                                        <th>Adresse</th>
                                        <td>{{ vendeur.adresse }}</td>
                                    </tr>
                                    <tr>
                                        <th>Code INSEE</th>
                                        <td></td>
                                    </tr>
                                    <tr>
                                        <th>Effectifs</th>
                                        <td>{{ vendeur.effectifs }} (en {{ vendeur.date_effectifs }})</td>
                                    </tr>
                                </tbody>
                            </table>
                        </TabPanel>
                        <TabPanel value="siege">
                            <table class="w-full">
                                <tbody>
                                    <tr>
                                        <th>Dénomination</th>
                                        <td>{{ vendeur.nom }}</td>
                                    </tr>
                                    <tr>
                                        <th>Date création</th>
                                        <td></td>
                                    </tr>
                                    <tr>
                                        <th>Sigle</th>
                                        <td>{{ vendeur.sigle }}</td>
                                    </tr>
                                    <tr>
                                        <th>Cat entreprise</th>
                                        <td>{{ getCatEntreprise(vendeur.cat_entreprise) }}</td>
                                    </tr>
                                    <tr>
                                        <th>Cat juridique</th>
                                        <td>{{ vendeur.cat_juridique }}</td>
                                    </tr>
                                    <tr>
                                        <th>NAF</th>
                                        <td>{{ vendeur.naf }}</td>
                                    </tr>
                                    <tr>
                                        <th>Effectifs</th>
                                        <td>{{ vendeur.effectifs }} (en {{ vendeur.date_effectifs }})</td>
                                    </tr>
                                </tbody>
                            </table>
                        </TabPanel>
                        <TabPanel value="infogreffe">
                            <DataTable :value="vendeur.infogreffe">
                                <Column field="annee" header="Année"></Column>
                                <Column field="ca" header="Chiffre d'affaires">
                                    <template #body="{ data }">{{ formatCurrency(parseFloat(data.ca)) }}</template>
                                </Column>
                                <Column field="resultat" header="Résultat">
                                    <template #body="{ data }">{{ formatCurrency(parseFloat(data.resultat)) }}</template>
                                </Column>
                                <Column field="effectif" header="Effectif">
                                    <template #body="{ data }">{{ formatNumber(data.effectif) }}</template>
                                </Column>
                            </DataTable>
                            <p class="text-sm">
                                L'accès aux données de certaines entreprises est confidentiel et n'est pas communiqué par Infogreffe. Voir la fiche complète sur
                                <Button
                                    icon="pi pi-external-link"
                                    label="infogreffe"
                                    aria-label="profil infogreffe"
                                    as="a"
                                    :href="'https://www.infogreffe.fr/infogreffe/ficheIdentite.do?siren=' + vendeur.identifiant?.substring(0, 9)"
                                    target="_blank"
                                    rel="noopener"
                                    severity="info"
                                    variant="text"
                                    size="small"
                                />.
                            </p>
                        </TabPanel>
                    </TabPanels>
                </Tabs>

                <div class="text-center mt-5">
                    <Button
                        icon="pi pi-search"
                        label="Voir la fiche annuaire d'entreprise"
                        aria-label="Annuaire"
                        as="a"
                        :href="'https://annuaire-entreprises.data.gouv.fr/etablissement/' + vendeur.identifiant"
                        target="_blank"
                        rel="noopener"
                        severity="info"
                        variant="outlined"
                    />
                </div>
            </div>
        </div>
    </section>
</template>

<style scoped>
table th {
    font-size: 0.8rem;
    text-transform: uppercase;
    text-align: left;
    font-weight: normal;
}

table td,
table th {
    padding: 0.5rem;
}
table tr:nth-child(2n) {
    border-top: 1px solid var(--p-neutral-300);
    border-bottom: 1px solid var(--p-neutral-300);
    background-color: var(--p-neutral-100);
}
</style>
