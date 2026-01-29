<script setup lang="ts">
import { CategorieMarche, listAcheteurs, listVendeurs } from '@/client';
import { getAcheteurUid } from '@/service/GetAcheteurService';
import { okabe_ito } from '@/service/GraphColorsService';
import { breakLongLabel, formatCurrency, formatNumber, getDurationInMonths, getNow, structureName } from '@/service/HelpersService';
import { onMounted, ref, watch } from 'vue';

import type { StructureAggMarchesDto } from '@/client';
import type { Layout, PlotData } from 'plotly.js-dist';

const props = defineProps({
    type: String,
    acheteurUid: { type: [Number, null], default: null },
    acheteurSiret: { type: [String, null], default: null },
    vendeurUid: { type: [Number, null], default: null },
    dateMin: { type: Date, default: new Date(settings.date_min) },
    dateMax: { type: Date, default: getNow() }
});

const listeStructures = ref({
    tout: [] as StructureAggMarchesDto[],
    services: [] as StructureAggMarchesDto[],
    travaux: [] as StructureAggMarchesDto[],
    fournitures: [] as StructureAggMarchesDto[]
});

const listeExhaustiveStructures = ref<StructureAggMarchesDto[]>([]);

let title = '';
let description = '';
let btn_label = '';
let link_path = '';

if (props.type == 'acheteurs') {
    title = 'Qui achète ?';
    description = 'Top 12 des acheteurs classés par montant total des contrats conclus au cours des ' + getDurationInMonths(props.dateMin, props.dateMax) + ' derniers mois. Survolez les noms les acheteurs pour les afficher en entier.';
    btn_label = 'Liste complète des organismes acheteurs';
    link_path = '/acheteur/';
} else {
    title = 'Qui réalise ?';
    description = 'Top 12 des fournisseurs classés par montant total des contrats remportés au cours des ' + getDurationInMonths(props.dateMin, props.dateMax) + ' derniers mois. Survolez les noms des fournisseurs pour les afficher en entier.';
    btn_label = 'Liste complète des fournisseurs';
    link_path = '/fournisseur/';
}

const data = ref({
    tout: [] as Partial<PlotData>[],
    services: [] as Partial<PlotData>[],
    travaux: [] as Partial<PlotData>[],
    fournitures: [] as Partial<PlotData>[]
});
const layout = {
    margin: { t: 0, b: 200, r: 100 },
    xaxis: {
        tickangle: 45
    }
} as Partial<Layout>;

function transform(input: Array<StructureAggMarchesDto>) {
    let output = {
        structures: [] as Array<string | null>,
        montants: [] as Array<string>
    };
    for (var line of input) {
        output.structures.push(breakLongLabel(structureName(line.structure), 30));
        output.montants.push(line.montant);
    }
    return output;
}

async function fetchData(categorie: CategorieMarche | undefined = undefined, exhaustif: boolean = false) {
    if (props.acheteurUid == -1) {
        return;
    }
    const acheteurUid = await getAcheteurUid(props.acheteurUid, props.acheteurSiret);
    (props.type == 'acheteurs' ? listAcheteurs : listVendeurs)({
        query: {
            limit: exhaustif ? null : 12,
            acheteur_uid: acheteurUid,
            vendeur_uid: props.vendeurUid,
            date_debut: props.dateMin,
            date_fin: props.dateMax,
            categorie: categorie
        }
    }).then((response) => {
        if (response.data) {
            if (exhaustif) {
                listeExhaustiveStructures.value = response.data.items;
            } else {
                listeStructures.value[categorie ? categorie.toLowerCase() : 'tout'] = response.data.items;
                let rawData = transform(response.data.items);
                data.value[categorie ? categorie.toLowerCase() : 'tout'] = [
                    {
                        x: rawData.structures,
                        y: rawData.montants,
                        type: 'bar',
                        marker: { color: okabe_ito, line: { color: okabe_ito, width: 1 } }
                    }
                ];
            }
        }
    });
}

onMounted(() => {
    fetchData();
});

// on garde trace de l'onglet sélectionné pour savoir quoi mettre à jour
let selectedTab = 'tout';

watch([() => props.dateMin, () => props.dateMax, () => props.acheteurUid, () => props.vendeurUid], () => {
    data.value = { tout: [], services: [], travaux: [], fournitures: [] };
    fetchData();
    if (selectedTab != 'tout') {
        fetchData(selectedTab as CategorieMarche);
    }
});

function change(categorie: string | number) {
    selectedTab = categorie as CategorieMarche;
    if (categorie != 'tout' && typeof categorie === 'string' && !data.value[categorie.toLowerCase()].length) {
        fetchData(categorie as CategorieMarche);
    }
}

const showModale = ref(false);

function openModale() {
    showModale.value = true;
    // on recharge systématiquement à l'ouverture au cas où les filtres auraient changé
    fetchData(undefined, true);
}
</script>

<template>
    <section>
        <h2 class="title">{{ title }}</h2>
        <p class="subtitle">{{ description }}</p>
        <Tabs value="tout" @update:value="change">
            <TabList>
                <Tab value="tout">Tous les marchés</Tab>
                <Tab :value="CategorieMarche.SERVICES">{{ CategorieMarche.SERVICES }}</Tab>
                <Tab :value="CategorieMarche.TRAVAUX">{{ CategorieMarche.TRAVAUX }}</Tab>
                <Tab :value="CategorieMarche.FOURNITURES">{{ CategorieMarche.FOURNITURES }}</Tab>
            </TabList>
            <TabPanels>
                <TabPanel value="tout">
                    <div class="flex flex-row gap-5">
                        <table class="basis-1/3 border-collapse text-right">
                            <tbody>
                                <tr v-for="line in listeStructures.tout" :key="line.structure.uid">
                                    <th>{{ structureName(line.structure) }}</th>
                                    <td>{{ formatCurrency(parseFloat(line.montant)) }}</td>
                                </tr>
                            </tbody>
                        </table>
                        <div class="basis-2/3">
                            <Graph :data="data.tout" :layout style="min-height: 25rem" />
                        </div>
                    </div>
                </TabPanel>
                <TabPanel :value="CategorieMarche.SERVICES">
                    <div class="flex flex-row gap-5">
                        <table class="basis-1/3 border-collapse text-right">
                            <tbody>
                                <tr v-for="line in listeStructures.services" :key="line.structure.uid">
                                    <th>{{ structureName(line.structure) }}</th>
                                    <td>{{ formatCurrency(parseFloat(line.montant)) }}</td>
                                </tr>
                            </tbody>
                        </table>
                        <div class="basis-2/3">
                            <Graph :data="data.services" :layout style="min-height: 25rem" />
                        </div>
                    </div>
                </TabPanel>
                <TabPanel :value="CategorieMarche.TRAVAUX">
                    <div class="flex flex-row gap-5">
                        <table class="basis-1/3 border-collapse text-right">
                            <tbody>
                                <tr v-for="line in listeStructures.travaux" :key="line.structure.uid">
                                    <th>{{ structureName(line.structure) }}</th>
                                    <td>{{ formatCurrency(parseFloat(line.montant)) }}</td>
                                </tr>
                            </tbody>
                        </table>
                        <div class="basis-2/3">
                            <Graph :data="data.travaux" :layout style="min-height: 25rem" />
                        </div>
                    </div>
                </TabPanel>
                <TabPanel :value="CategorieMarche.FOURNITURES">
                    <div class="flex flex-row gap-5">
                        <table class="basis-1/3 border-collapse text-right">
                            <tbody>
                                <tr v-for="line in listeStructures.fournitures" :key="line.structure.uid">
                                    <th>{{ structureName(line.structure) }}</th>
                                    <td>{{ formatCurrency(parseFloat(line.montant)) }}</td>
                                </tr>
                            </tbody>
                        </table>
                        <div class="basis-2/3">
                            <Graph :data="data.fournitures" :layout style="min-height: 25rem" />
                        </div>
                    </div>
                </TabPanel>
            </TabPanels>
        </Tabs>
        <div class="flex flex-wrap">
            <Button :label="btn_label" variant="text" severity="secondary" icon="pi pi-list" aria-label="Voir la liste des structures" @click="openModale" />
        </div>
        <BoutonIframe v-if="acheteurSiret" :path="'acheteur/' + acheteurSiret + '/marches/top12'" name="Le top12 des fournisseurs" />
    </section>
    <Dialog :visible="showModale" modal :header="btn_label" class="max-w-full" @update:visible="showModale = false">
        <DataTable :value="listeExhaustiveStructures" sortField="structure.nom" :sortOrder="1" removableSort stripedRows paginator :rows="10">
            <Column field="structure.nom" header="Nom" sortable>
                <template #body="slotProps">
                    <RouterLink :to="link_path + slotProps.data.structure.uid">
                        <Button :label="structureName(slotProps.data.structure)" as="a" variant="link" />
                    </RouterLink>
                </template>
            </Column>
            <Column field="nb_contrats" header="NB contrats" sortable>
                <template #body="{ data }">
                    {{ formatNumber(data.nb_contrats) }}
                </template>
            </Column>
            <Column field="montant" header="Montant contrats" sortable bodyStyle="text-align:right">
                <template #body="{ data }">
                    {{ formatCurrency(parseFloat(data.montant)) }}
                </template>
            </Column>
        </DataTable>
    </Dialog>
</template>
