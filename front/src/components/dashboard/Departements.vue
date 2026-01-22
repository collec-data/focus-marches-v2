<script setup lang="ts">
import { getMarchesParDepartement } from '@/client';
import { getNomDepartement } from '@/service/Departements';
import { okabe_ito } from '@/service/GraphColorsService';
import { onMounted, ref } from 'vue';

import type { MarcheDepartementDto } from '@/client';
import type { Layout, PlotData } from 'plotly.js-dist';

const montantRegion = ref<Partial<PlotData>[]>();
const nombreRegion = ref<Partial<PlotData>[]>();
const montantHorsRegion = ref<Partial<PlotData>[]>();
const nombreHorsRegion = ref<Partial<PlotData>[]>();
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
    const output = {
        departements: [] as Array<string>,
        montants: [] as Array<number>,
        nombres: [] as Array<number>
    };
    const outputHorsRegion = {
        departements: [] as Array<string>,
        montants: [] as Array<number>,
        nombres: [] as Array<number>
    };
    const departementsRegion = settings.departements.split(',');
    for (var line of input) {
        const nom_departement = getNomDepartement(line.code);
        if (nom_departement) {
            if (departementsRegion.includes(line.code)) {
                output.departements.push('(' + line.code + ') ' + nom_departement);
                output.montants.push(parseFloat(line.montant));
                output.nombres.push(line.nombre);
            } else {
                outputHorsRegion.departements.push('(' + line.code + ') ' + nom_departement);
                outputHorsRegion.montants.push(parseFloat(line.montant));
                outputHorsRegion.nombres.push(line.nombre);
            }
        }
    }

    output.departements.unshift('Hors région');
    output.montants.unshift(outputHorsRegion.montants.reduce((partialSum, a) => partialSum + a, 0));
    output.nombres.unshift(outputHorsRegion.nombres.reduce((partialSum, a) => partialSum + a, 0));
    return { region: output, horsRegion: outputHorsRegion };
}

onMounted(() => {
    getMarchesParDepartement().then((response) => {
        if (response.data) {
            const { region, horsRegion } = transform(response.data);
            montantRegion.value = makeGraph(region.departements, region.montants);
            nombreRegion.value = makeGraph(region.departements, region.nombres);
            montantHorsRegion.value = makeGraph(horsRegion.departements, horsRegion.montants);
            nombreHorsRegion.value = makeGraph(horsRegion.departements, horsRegion.nombres);
        }
    });
});
</script>

<template>
    <section>
        <h2 class="title">Contrats par départements</h2>
        <Tabs value="region">
            <TabList>
                <Tab value="region">Dans la région</Tab>
                <Tab value="hors-region">Hors région</Tab>
            </TabList>
            <TabPanels>
                <TabPanel value="region">
                    <div class="grid grid-cols-12 gap-8">
                        <div class="col-span-12 xl:col-span-6">
                            <h3>Montant des contrats par département</h3>
                            <Graph :data="montantRegion" :layout />
                        </div>
                        <div class="col-span-12 xl:col-span-6">
                            <h3>Nombre de contrats par département</h3>
                            <Graph :data="nombreRegion" :layout />
                        </div>
                    </div>
                </TabPanel>
                <TabPanel value="hors-region">
                    <div class="grid grid-cols-12 gap-8">
                        <div class="col-span-12 xl:col-span-6">
                            <h3>Montant des contrats par département</h3>
                            <Graph :data="montantHorsRegion" :layout />
                        </div>
                        <div class="col-span-12 xl:col-span-6">
                            <h3>Nombre de contrats par département</h3>
                            <Graph :data="nombreHorsRegion" :layout />
                        </div>
                    </div>
                </TabPanel>
            </TabPanels>
        </Tabs>
        <details>
            <summary>💡 Pourquoi des contrats hors-région ?</summary>
            <div>
                <h3>Contrats hors région</h3>
                <p>
                    Ce faible montant de contrats hors région n'est pas une anomalie. Il peut s'agir de prestations commandées lors d'un déplacement ou un salon par exemple, ou d'un marché sur une aire géographique couvrant plusieurs régions à la
                    fois.
                </p>
            </div>
        </details>
    </section>
</template>
