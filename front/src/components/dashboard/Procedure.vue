<script setup lang="ts">
import { getMarchesParProcedure } from '@/client';
import { getDurationInMonths, longLabelsBreaker } from '@/service/HelpersService';
import { onMounted, ref, watch } from 'vue';
import Graph from '../Graph.vue';

import type { MarcheProcedureDto } from '@/client';
import { okabe_ito } from '@/service/GraphColorsService';
import type { Layout, PlotData } from 'plotly.js-dist';

const props = defineProps({
    acheteurUid: { type: [String, null], default: null },
    vendeurUid: { type: [String, null], default: null },
    dateMin: { type: Date, required: true },
    dateMax: { type: Date, required: true }
});

const montantData = ref<Partial<PlotData>[]>();
const nombreData = ref<Partial<PlotData>[]>();
const layout = { margin: { l: 130, t: 0, b: 20, r: 0 } } as Layout;

function transform(input: Array<MarcheProcedureDto>) {
    let output = {
        procedure: [] as Array<string | null>,
        montant: [] as Array<number>,
        nombre: [] as Array<number>
    };
    for (var line of input) {
        output.procedure.push(line.procedure);
        output.montant.push(parseFloat(line.montant));
        output.nombre.push(line.nombre);
    }
    return output;
}

function makeGraph(labels: Array<string | null>, data: Array<number>): Partial<PlotData>[] {
    return [
        {
            y: longLabelsBreaker(labels),
            x: data,
            type: 'bar',
            orientation: 'h',
            marker: { color: okabe_ito, line: { color: okabe_ito, width: 1 } }
        }
    ];
}

function fetchData() {
    getMarchesParProcedure({
        query: {
            date_debut: props.dateMin,
            date_fin: props.dateMax,
            acheteur_uid: props.acheteurUid,
            vendeur_uid: props.vendeurUid
        }
    }).then((data) => {
        if (data.data) {
            let raw_data = transform(data.data);
            montantData.value = makeGraph(raw_data.procedure, raw_data.montant);
            nombreData.value = makeGraph(raw_data.procedure, raw_data.nombre);
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
    <Fluid class="grid grid-cols-12 gap-8">
        <div class="col-span-12">
            <h2 class="title">Procédure suivie</h2>
            <p class="subtitle">Classement des contrats selon la procédure suivie lors de la consultation. La période observée est de {{ getDurationInMonths(dateMin, dateMax) }} mois</p>
        </div>
        <div class="col-span-12 xl:col-span-6">
            <h3>Montant des contrats par procédure</h3>
            <Graph :data="montantData" :layout />
        </div>
        <div class="col-span-12 xl:col-span-6">
            <h3>Nombre des contrats par procédure</h3>
            <Graph :data="nombreData" :layout />
        </div>
        <div class="col-span-12">
            <BoutonIframe v-if="acheteurUid" :acheteurUid path="procedure-marches" name="La répartition des marchés publics par procédure suivie, sous forme de graphique" />
        </div>
    </Fluid>
</template>
