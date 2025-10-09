<script setup lang="ts">
import { getMarchesParCcagMarcheCcagGet } from '@/client';
import Plotly from 'plotly.js-dist';
import { onBeforeUnmount, onMounted, useId, watch } from 'vue';

import type { MarcheCcagDto } from '@/client';

const props = defineProps({
    acheteurUid: { type: [String, null], default: null },
    dateMin: { type: [Date, null], default: null },
    dateMax: { type: [Date, null], default: null }
});

const graphMontantId = useId();
const graphNombreId = useId();

function transform(input: Array<MarcheCcagDto>) {
    let output = {
        ccags: [] as Array<string>,
        montants: [] as Array<number>,
        nombres: [] as Array<number>
    };
    for (var line of input) {
        if (line.ccag) {
            output.ccags.push(line.ccag.toString());
        } else {
            output.ccags.push('Sans CCAG');
        }
        output.montants.push(parseFloat(line.montant));
        output.nombres.push(line.nombre);
    }
    return output;
}

function makeGraph(graphId: string, labels: Array<string | null>, data: Array<number>) {
    Plotly.newPlot(
        graphId,
        [
            {
                y: labels,
                x: data,
                type: 'bar',
                orientation: 'h'
            }
        ],
        { margin: { l: 10, t: 0, b: 20, r: 0 } }
    );
}

function fetchData() {
    getMarchesParCcagMarcheCcagGet({
        query: {
            date_debut: props.dateMin,
            date_fin: props.dateMax,
            acheteur_uid: props.acheteurUid
        }
    }).then((response) => {
        if (response.data) {
            let data = transform(response.data);
            makeGraph(graphMontantId, data.ccags, data.montants);
            makeGraph(graphNombreId, data.ccags, data.nombres);
        }
    });
}

function purgeGraphs() {
    Plotly.purge(graphMontantId);
    Plotly.purge(graphNombreId);
}

onMounted(() => {
    fetchData();
});

watch([() => props.dateMin, () => props.dateMax, () => props.acheteurUid], () => {
    purgeGraphs();
    fetchData();
});

onBeforeUnmount(() => {
    purgeGraphs();
});
</script>

<template>
    <section>
        <h2 class="title">Cahier des clauses administratives et générales utilisés</h2>
        <div class="grid grid-cols-12 gap-8">
            <div class="col-span-12 xl:col-span-6">
                <h3>Montant des contrats par CCAG</h3>
                <div :id="graphMontantId" class="aspect-4/3"></div>
            </div>
            <div class="col-span-12 xl:col-span-6">
                <h3>Nombre de contrats par CCAG</h3>
                <div :id="graphNombreId" class="aspect-4/3"></div>
            </div>
        </div>
    </section>
</template>
