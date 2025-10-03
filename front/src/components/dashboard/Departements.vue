<script setup lang="ts">
import { getMarchesParDepartementMarcheDepartementGet } from '@/client';
import { getNomDepartement } from '@/service/Departements';
import Plotly from 'plotly.js-dist';
import { onBeforeUnmount, onMounted, useId } from 'vue';

import type { MarcheDepartementDto } from '@/client';

const graphMontantId = useId();
const graphNombreId = useId();

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
        { margin: { l: 150, t: 0, b: 20, r: 0 } }
    );
}

function transform(input: Array<MarcheDepartementDto>) {
    let output = {
        departements: [] as Array<string>,
        montants: [] as Array<number>,
        nombres: [] as Array<number>
    };
    for (var line of input) {
        output.departements.push('(' + line.code + ') ' + getNomDepartement(line.code));
        output.montants.push(parseFloat(line.montant));
        output.nombres.push(line.nombre);
    }
    return output;
}

onMounted(() => {
    getMarchesParDepartementMarcheDepartementGet().then((response) => {
        if (response.data) {
            let data = transform(response.data);
            makeGraph(graphMontantId, data.departements, data.montants);
            makeGraph(graphNombreId, data.departements, data.nombres);
        }
    });
});

onBeforeUnmount(() => {
    Plotly.purge(graphMontantId);
    Plotly.purge(graphNombreId);
});
</script>

<template>
    <section>
        <h2 class="title">Contrats par départements</h2>
        <div class="grid grid-cols-12 gap-8">
            <div class="col-span-12 xl:col-span-6">
                <h3>Montant des contrats par département</h3>
                <div :id="graphMontantId" class="aspect-4/3"></div>
            </div>
            <div class="col-span-12 xl:col-span-6">
                <h3>Nombre de contrats par département</h3>
                <div :id="graphNombreId" class="aspect-4/3"></div>
            </div>
        </div>
    </section>
</template>
