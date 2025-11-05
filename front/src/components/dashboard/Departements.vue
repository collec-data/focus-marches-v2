<script setup lang="ts">
import { getMarchesParDepartementMarcheDepartementGet } from '@/client';
import { getNomDepartement } from '@/service/Departements';
import { onMounted, ref } from 'vue';

import type { MarcheDepartementDto } from '@/client';
import { okabe_ito } from '@/service/GraphColorsService';
import type { Layout, PlotData } from 'plotly.js-dist';

const montaData = ref<Partial<PlotData>[]>();
const nombreData = ref<Partial<PlotData>[]>();
const layout = { margin: { l: 150, t: 0, b: 20, r: 0 } } as Partial<Layout>;

function makeGraph(labels: Array<string | null>, data: Array<number>): Array<Partial<PlotData>> {
    return [
        {
            y: labels,
            x: data,
            type: 'bar',
            orientation: 'h',
            marker: { color: okabe_ito, line: { color: okabe_ito, width: 1 } }
        }
    ];
}

function transform(input: Array<MarcheDepartementDto>) {
    let output = {
        departements: [] as Array<string>,
        montants: [] as Array<number>,
        nombres: [] as Array<number>
    };
    for (var line of input) {
        const nom_departement = getNomDepartement(line.code);
        if (nom_departement) {
            output.departements.push('(' + line.code + ') ' + nom_departement);
            output.montants.push(parseFloat(line.montant));
            output.nombres.push(line.nombre);
        }
    }
    return output;
}

onMounted(() => {
    getMarchesParDepartementMarcheDepartementGet().then((response) => {
        if (response.data) {
            let data = transform(response.data);
            montaData.value = makeGraph(data.departements, data.montants);
            nombreData.value = makeGraph(data.departements, data.nombres);
        }
    });
});
</script>

<template>
    <section>
        <h2 class="title">Contrats par départements</h2>
        <div class="grid grid-cols-12 gap-8">
            <div class="col-span-12 xl:col-span-6">
                <h3>Montant des contrats par département</h3>
                <Graph :data="montaData" :layout />
            </div>
            <div class="col-span-12 xl:col-span-6">
                <h3>Nombre de contrats par département</h3>
                <Graph :data="nombreData" :layout />
            </div>
        </div>
    </section>
</template>
