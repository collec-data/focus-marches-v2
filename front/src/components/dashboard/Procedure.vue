<script setup lang="ts">
import { getMarchesParProcedureMarcheProcedureGet } from '@/client';

import type { MarcheProcedureDto } from '@/client';
import Plotly from 'plotly.js-dist';
import { onBeforeUnmount, onMounted } from 'vue';

const props = defineProps({
    acheteurUid: { type: [String, null], default: null },
    vendeurUid: { type: [String, null], default: null }
});

const graphMontantsId = 'graph-montants';
const graphNombresId = 'graph-nombre';

function transform(input: Array<MarcheProcedureDto>) {
    let output = {
        procedure: [] as Array<number | null>,
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

function makeGraph(graphId: string, labels: Array<number | null>, data: Array<number>) {
    Plotly.newPlot(graphId, [
        {
            y: labels,
            x: data,
            type: 'bar',
            orientation: 'h'
        }
    ]);
}

onMounted(() => {
    getMarchesParProcedureMarcheProcedureGet({
        query: {
            date_debut: new Date('2010-01-01'),
            acheteur_uid: props.acheteurUid,
            vendeur_uid: props.vendeurUid
        }
    }).then((data) => {
        if (data.data) {
            let raw_data = transform(data.data);
            makeGraph(graphMontantsId, raw_data.procedure, raw_data.montant);
            makeGraph(graphNombresId, raw_data.procedure, raw_data.nombre);
        }
    });
});

onBeforeUnmount(() => {
    Plotly.purge(graphMontantsId);
    Plotly.purge(graphNombresId);
});
</script>

<template>
    <Fluid class="grid grid-cols-12 gap-8">
        <div class="col-span-12">
            <h2 class="title">Procédure suivie</h2>
            <p class="subtitle">Classement des contrats selon la procédure suivie lors de la consultation. La période observée est de XX mois</p>
        </div>
        <div class="col-span-12 xl:col-span-6">
            <h3>Montant des contrats par procédure</h3>
            <div id="graph-montants"></div>
        </div>
        <div class="col-span-12 xl:col-span-6">
            <h3>Nombre des contrats par procédure</h3>
            <div id="graph-nombre"></div>
        </div>
    </Fluid>
</template>
