<script setup lang="ts">
import { CategorieMarche, listAcheteursStructureAcheteurGet, listVendeursStructureVendeurGet } from '@/client';
import { okabe_ito } from '@/service/GraphColorsService';
import { formatCurrency, structureName } from '@/service/HelpersService';
import { onMounted, ref } from 'vue';

import type { StructureAggMarchesDto } from '@/client';
import type { Layout, PlotData } from 'plotly.js-dist';

const props = defineProps({
    type: String,
    acheteurUid: { type: [String, null], default: null },
    vendeurUid: { type: [String, null], default: null },
    dateMin: { type: [Date, null], default: null },
    dateMax: { type: [Date, null], default: null }
});

const listeStructures = ref({
    tout: [] as StructureAggMarchesDto[],
    services: [] as StructureAggMarchesDto[],
    travaux: [] as StructureAggMarchesDto[],
    fournitures: [] as StructureAggMarchesDto[]
});

let title = '';
let description = '';
let btn_label = '';

if (props.type == 'acheteurs') {
    title = 'Qui achète ?';
    description = 'Top 12 des acheteurs classés par montant total des contrats conclus au cours des 56 derniers mois. Survolez les noms les acheteurs pour les afficher en entier.';
    btn_label = 'Liste complète des organismes acheteurs';
} else {
    title = 'Qui réalise ?';
    description = 'Top 12 des fournisseurs classés par montant total des contrats remportés au cours des 56 derniers mois. Survolez les noms des fournisseurs pour les afficher en entier.';
    btn_label = 'Liste complète des fournisseurs';
}

const data = ref({
    tout: [] as Partial<PlotData>[],
    services: [] as Partial<PlotData>[],
    travaux: [] as Partial<PlotData>[],
    fournitures: [] as Partial<PlotData>[]
});
const layout = { margin: { t: 0 } } as Partial<Layout>;

function transform(input: Array<StructureAggMarchesDto>) {
    let output = {
        structures: [] as Array<string | null>,
        montants: [] as Array<string>
    };
    for (var line of input) {
        output.structures.push(structureName(line.structure));
        output.montants.push(line.montant);
    }
    return output;
}

function fetchData(categorie: CategorieMarche | undefined = undefined) {
    (props.type == 'acheteurs' ? listAcheteursStructureAcheteurGet : listVendeursStructureVendeurGet)({
        query: {
            limit: 12,
            acheteur_uid: props.acheteurUid ? parseInt(props.acheteurUid) : null,
            vendeur_uid: props.vendeurUid ? parseInt(props.vendeurUid) : null,
            date_debut: props.dateMin,
            date_fin: props.dateMax,
            categorie: categorie
        }
    }).then((response) => {
        if (response.data) {
            listeStructures.value[categorie ? categorie.toLowerCase() : 'tout'] = response.data;
            let rawData = transform(response.data);
            data.value[categorie ? categorie.toLowerCase() : 'tout'] = [
                {
                    x: rawData.structures,
                    y: rawData.montants,
                    type: 'bar',
                    marker: { color: okabe_ito, line: { color: okabe_ito, width: 1 } }
                }
            ];
        }
    });
}

onMounted(() => {
    fetchData();
});

function change(categorie: string | number) {
    if (categorie != 'tout' && typeof categorie === 'string' && !data.value[categorie.toLowerCase()].length) {
        fetchData(categorie as CategorieMarche);
    }
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
                        <Graph :data="data.tout" :layout style="min-height: 20rem" />
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
                        <Graph :data="data.services" :layout style="min-height: 20rem" />
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
                        <Graph :data="data.travaux" :layout style="min-height: 20rem" />
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
                        <Graph :data="data.fournitures" :layout style="min-height: 20rem" />
                    </div>
                </TabPanel>
            </TabPanels>
        </Tabs>
        <div class="flex flex-wrap">
            <RouterLink to="/acheteurs">
                <Button :label="btn_label" variant="text" severity="secondary" icon="pi pi-list" />
            </RouterLink>
        </div>
    </section>
</template>
