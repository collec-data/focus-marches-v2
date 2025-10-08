<script setup lang="ts">
import { getMarchesParCcagMarcheCcagGet } from '@/client';
import { longLabelsBreaker } from '@/service/HelpersService';
import { onMounted, ref, watch } from 'vue';

import type { MarcheCcagDto } from '@/client';
import type { Layout, PlotData } from 'plotly.js-dist';

const props = defineProps({
    acheteurUid: { type: [String, null], default: null },
    dateMin: { type: [Date, null], default: null },
    dateMax: { type: [Date, null], default: null }
});

const montantData = ref<Partial<PlotData>[]>();
const nombreData = ref<Partial<PlotData>[]>();
const layout = { margin: { l: 150, t: 0, b: 20, r: 0 } } as Layout;

function transform(input: Array<MarcheCcagDto>) {
    let output = {
        ccags: [] as Array<string>,
        montants: [] as Array<number>,
        nombres: [] as Array<number>
    };
    for (var line of input) {
        if (line.ccag) {
            output.ccags.push(line.ccag);
        } else {
            output.ccags.push('Sans CCAG');
        }
        output.montants.push(parseFloat(line.montant));
        output.nombres.push(line.nombre);
    }
    return output;
}

function makeGraph(labels: Array<string | null>, data: Array<number>): Partial<PlotData>[] {
    return [
        {
            y: longLabelsBreaker(labels, 11),
            x: data,
            type: 'bar',
            orientation: 'h'
        }
    ];
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
            montantData.value = makeGraph(data.ccags, data.montants);
            nombreData.value = makeGraph(data.ccags, data.nombres);
        }
    });
}

onMounted(() => {
    fetchData();
});

watch([() => props.dateMin, () => props.dateMax, () => props.acheteurUid], () => {
    fetchData();
});
</script>

<template>
    <section>
        <h2 class="title">Cahier des clauses administratives et générales utilisés</h2>
        <div class="grid grid-cols-12 gap-8">
            <div class="col-span-12 xl:col-span-6">
                <h3>Montant des contrats par CCAG</h3>
                <Graph :data="montantData" :layout />
            </div>
            <div class="col-span-12 xl:col-span-6">
                <h3>Nombre de contrats par CCAG</h3>
                <Graph :data="nombreData" :layout />
            </div>
        </div>
    </section>
</template>
