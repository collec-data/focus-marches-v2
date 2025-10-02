<script setup lang="ts">
import type { MarcheNatureDto } from '@/client';
import { getMarchesParNatureMarcheNatureGet } from '@/client';
import { formatCurrency } from '@/service/HelpersService';
import Plotly from 'plotly.js-dist';
import { onMounted, onUnmounted, ref } from 'vue';

const props = defineProps({
    acheteurUid: { type: [String, null], default: null },
    vendeurUid: { type: [String, null], default: null }
});

const stats = ref([
    { montant_total: 0, nombre_total: 0 },
    { montant_total: 0, nombre_total: 0 },
    { montant_total: 0, nombre_total: 0 }
]);

function transform(input: Array<MarcheNatureDto>) {
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

const graphMarcheId = 'graph-marche';
const graphPartenariatId = 'graph-partenariat';
const graphDefenseId = 'graph-defense';

onMounted(() => {
    getMarchesParNatureMarcheNatureGet({
        query: {
            date_debut: new Date('2010-01-01'),
            acheteur_uid: props.acheteurUid,
            vendeur_uid: props.vendeurUid
        }
    }).then((data) => {
        if (data.data) {
            let rawData = transform(data.data);
            Plotly.newPlot(
                graphMarcheId,
                [
                    {
                        x: rawData[0].labels,
                        y: rawData[0].values,
                        type: 'bar'
                    }
                ],
                {},
                { displayModeBar: false }
            );
            Plotly.newPlot(
                graphPartenariatId,
                [
                    {
                        x: rawData[1].labels,
                        y: rawData[1].values,
                        type: 'bar'
                    }
                ],
                {},
                { displayModeBar: false }
            );
            Plotly.newPlot(
                graphDefenseId,
                [
                    {
                        x: rawData[2].labels,
                        y: rawData[2].values,
                        type: 'bar'
                    }
                ],
                {},
                { displayModeBar: false }
            );
        }
    });
});

onUnmounted(() => {
    Plotly.purge(graphMarcheId);
    Plotly.purge(graphPartenariatId);
    Plotly.purge(graphDefenseId);
});
</script>

<template>
    <section class="flex flex-col">
        <h2 class="title">Nature des contrats</h2>
        <p>Répartition des contrats par nature du marché public, en montant et en nombre. La période observée est de XX mois et les marchés sont groupés par mois.</p>
        <div class="flex flex-row gap-5 flex-wrap">
            <div class="nature basis-1/3">
                <h3>Marché</h3>
                <div id="graph-marche" class="chart"></div>
                <ul>
                    <li><span>Montant</span> {{ formatCurrency(stats[0].montant_total) }}</li>
                    <li><span>Nombre</span> {{ stats[0].nombre_total }} marchés</li>
                </ul>
            </div>
            <div class="nature basis-1/3">
                <h3>Marché de partenariat</h3>
                <div id="graph-partenariat" class="chart"></div>
                <ul>
                    <li><span>Montant</span> {{ formatCurrency(stats[1].montant_total) }}</li>
                    <li><span>Nombre</span> {{ stats[1].nombre_total }} marchés</li>
                </ul>
            </div>
            <div class="nature basis-1/3">
                <h3>Marché de défense ou de sécurité</h3>
                <div id="graph-defense" class="chart"></div>
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
    </section>
</template>

<style>
.nature {
    flex-basis: 0;
    flex-grow: 1;
    flex-shrink: 1;
}

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
