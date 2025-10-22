<script setup lang="ts">
import { getMarchesParNatureMarcheNatureGet } from '@/client';
import { formatCurrency } from '@/service/HelpersService';
import { onMounted, ref, watch } from 'vue';

import type { MarcheNatureDtoOutput } from '@/client';
import { okabe_ito } from '@/service/GraphColorsService';
import type Plotly from 'plotly.js-dist';

const props = defineProps({
    acheteurUid: { type: [String, null], default: null },
    vendeurUid: { type: [String, null], default: null },
    dateMin: { type: [Date, null], default: null },
    dateMax: { type: [Date, null], default: null }
});

const stats = ref([
    { montant_total: 0, nombre_total: 0 },
    { montant_total: 0, nombre_total: 0 },
    { montant_total: 0, nombre_total: 0 }
]);

function transform(input: Array<MarcheNatureDtoOutput>) {
    let output = [
        { labels: [] as Array<string>, values: [] as Array<number> },
        { labels: [] as Array<string>, values: [] as Array<number> },
        { labels: [] as Array<string>, values: [] as Array<number> }
    ];
    for (let line of input) {
        // les valeurs de `line.nature` vont de 1 à 3 -> on décale
        // pour se caler sur les tableaux dont les indices commencent à 0
        output[line.nature - 1].labels.push(line.mois);
        output[line.nature - 1].values.push(parseFloat(line.montant));
        stats.value[line.nature - 1].montant_total += parseFloat(line.montant);
        stats.value[line.nature - 1].nombre_total += line.nombre;
    }
    return output;
}

const marcheData = ref<Partial<Plotly.PlotData>[]>();
const partenariatData = ref<Partial<Plotly.Data>[]>();
const defenseData = ref<Partial<Plotly.Data>[]>();
const layout = { margin: { t: 0, r: 0, b: 20 } } as Partial<Plotly.Layout>;
const config = { displayModeBar: false } as Partial<Plotly.Config>;

function makeGraph(labels: Array<string | null>, data: Array<number>, color: string): Array<Partial<Plotly.PlotData>> {
    return [
        {
            x: labels,
            y: data,
            type: 'bar',
            marker: { color: color, line: { color: color, width: 1 } }
        }
    ];
}

function fetchData() {
    getMarchesParNatureMarcheNatureGet({
        query: {
            date_debut: props.dateMin,
            date_fin: props.dateMax,
            acheteur_uid: props.acheteurUid,
            vendeur_uid: props.vendeurUid
        }
    }).then((data) => {
        if (data.data) {
            let rawData = transform(data.data);
            marcheData.value = makeGraph(rawData[0].labels, rawData[0].values, okabe_ito[0]);
            partenariatData.value = makeGraph(rawData[1].labels, rawData[1].values, okabe_ito[1]);
            defenseData.value = makeGraph(rawData[2].labels, rawData[2].values, okabe_ito[2]);
        }
    });
}

onMounted(() => {
    fetchData();
});

watch([() => props.dateMin, () => props.dateMax, () => props.acheteurUid, () => props.vendeurUid], () => {
    fetchData();
});
</script>

<template>
    <section class="flex flex-col">
        <h2 class="title">Nature des contrats</h2>
        <p>Répartition des contrats par nature du marché public, en montant et en nombre. La période observée est de XX mois et les marchés sont groupés par mois.</p>
        <div class="flex flex-row gap-5 flex-wrap">
            <div class="nature basis-md grow shrink">
                <h3>Marché</h3>
                <Graph :data="marcheData" :layout :config />
                <ul>
                    <li><span>Montant</span> {{ formatCurrency(stats[0].montant_total) }}</li>
                    <li><span>Nombre</span> {{ stats[0].nombre_total }} marchés</li>
                </ul>
            </div>
            <div class="nature basis-md grow shrink">
                <h3>Marché de partenariat</h3>
                <Graph :data="partenariatData" :layout :config />
                <ul>
                    <li><span>Montant</span> {{ formatCurrency(stats[1].montant_total) }}</li>
                    <li><span>Nombre</span> {{ stats[1].nombre_total }} marchés</li>
                </ul>
            </div>
            <div class="nature basis-md grow shrink">
                <h3>Marché de défense ou de sécurité</h3>
                <Graph :data="defenseData" :layout :config />
                <ul>
                    <li><span>Montant</span> {{ formatCurrency(stats[2].montant_total) }}</li>
                    <li><span>Nombre</span> {{ stats[2].nombre_total }} marchés</li>
                </ul>
            </div>
        </div>
        <details>
            <summary>💡 Comment lire ces graphiques ?</summary>
            <div class="flex flex-row gap-10">
                <div class="basis-1/2">
                    <h3>Comment lire ces graphiques ?</h3>
                    <p>Les marchés publics sont répartis en quatre grandes natures de contrats :</p>
                    <ul>
                        <li>Marché : cas général, contrat entre un acheteur public et un fournisseur</li>
                        <li>Marché de partenariat : contrat spécifique qui « permet de confier à un opérateur économique ou à un groupement d’opérateurs économiques une mission globale » sous maîtrise d’ouvrage privée.</li>
                        <li>Marché de défense ou de sécurité :</li>
                    </ul>
                </div>

                <div class="basis-1/2">
                    <h3>Pour chaque catégorie il est indiqué :</h3>
                    <p>Le montant total, le nombre de contrats, un affichage de leur distribution temporelle. La hauteur des barres (axe Y) reflète le montant.</p>
                    <p>Vous pouvez survoler les graphiques avec votre souris pour plus d’informations.</p>
                </div>
            </div>
        </details>
        <BoutonIframe v-if="acheteurUid" :acheteurUid path="nature-marches" name="La répartition des marchés publics par nature, sous forme de graphique" />
    </section>
</template>

<style scoped>
.nature h3 {
    margin: 0;
}

.nature .chart {
    aspect-ratio: 4/3;
    width: 100%;
}

.nature ul span {
    display: inline-block;
    width: 50%;
    text-align: right;
    padding-right: 2rem;
    text-transform: uppercase;
    color: var(--p-primary-color);
    font-weight: bold;
}
</style>
