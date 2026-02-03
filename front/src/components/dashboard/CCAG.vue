<script setup lang="ts">
import { getMarchesParCcag } from '@/client';
import { getAcheteurUid } from '@/service/GetAcheteurService';
import { okabe_ito } from '@/service/GraphColorsService';
import { breakLongLabel } from '@/service/HelpersService';
import { onMounted, ref, watch } from 'vue';

import type { MarcheCcagDto } from '@/client';
import type { Layout, PlotData } from 'plotly.js-dist';

const props = defineProps({
    acheteurUid: { type: [Number, null], default: null },
    acheteurSiret: { type: [String, null], default: null },
    dateMin: { type: [Date, null], default: null },
    dateMax: { type: [Date, null], default: null }
});

interface icategorie {
    montants: Partial<PlotData>[];
    nombres: Partial<PlotData>[];
}
interface idatas {
    travaux: icategorie;
    services: icategorie;
    fournitures: icategorie;
}

const datas = ref<Partial<idatas>>({});
const layout = { margin: { l: 150, t: 0, b: 20, r: 0 } } as Layout;

function transform(input: Array<MarcheCcagDto>): idatas {
    const common = {
        type: 'bar',
        orientation: 'h',
        marker: { color: okabe_ito, line: { color: okabe_ito, width: 1 } }
    };
    let output = <idatas>{
        travaux: { montants: [{ x: [], y: [], ...common }], nombres: [{ x: [], y: [], ...common }] },
        services: { montants: [{ x: [], y: [], ...common }], nombres: [{ x: [], y: [], ...common }] },
        fournitures: { montants: [{ x: [], y: [], ...common }], nombres: [{ x: [], y: [], ...common }] }
    };
    for (var line of input) {
        const key = line.categorie.toLowerCase();
        if (line.ccag) {
            output[key].montants[0].y.push(breakLongLabel(line.ccag));
            output[key].nombres[0].y.push(breakLongLabel(line.ccag));
        } else {
            output[key].montants[0].y.push('Sans CCAG');
            output[key].nombres[0].y.push('Sans CCAG');
        }
        output[key].montants[0].x.push(parseFloat(line.montant));
        output[key].nombres[0].x.push(line.nombre);
    }
    return output;
}

async function fetchData() {
    if (props.acheteurUid == -1) {
        return;
    }
    const acheteurUid = await getAcheteurUid(props.acheteurUid, props.acheteurSiret);
    getMarchesParCcag({
        query: {
            date_debut: props.dateMin,
            date_fin: props.dateMax,
            acheteur_uid: acheteurUid
        }
    }).then((response) => {
        if (response.data) {
            datas.value = transform(response.data);
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
        <Tabs value="services">
            <TabList>
                <Tab value="services">Services</Tab>
                <Tab value="travaux">Travaux</Tab>
                <Tab value="fournitures">Fournitures</Tab>
            </TabList>
            <TabPanels>
                <TabPanel value="services">
                    <div class="grid grid-cols-12 gap-8">
                        <div class="col-span-12 xl:col-span-6">
                            <h3>Montant des contrats par CCAG</h3>
                            <Graph :data="datas.services?.montants" :layout />
                        </div>
                        <div class="col-span-12 xl:col-span-6">
                            <h3>Nombre de contrats par CCAG</h3>
                            <Graph :data="datas.services?.nombres" :layout />
                        </div>
                    </div>
                </TabPanel>
                <TabPanel value="travaux">
                    <div class="grid grid-cols-12 gap-8">
                        <div class="col-span-12 xl:col-span-6">
                            <h3>Montant des contrats par CCAG</h3>
                            <Graph :data="datas.travaux?.montants" :layout />
                        </div>
                        <div class="col-span-12 xl:col-span-6">
                            <h3>Nombre de contrats par CCAG</h3>
                            <Graph :data="datas.travaux?.nombres" :layout />
                        </div>
                    </div>
                </TabPanel>
                <TabPanel value="fournitures">
                    <div class="grid grid-cols-12 gap-8">
                        <div class="col-span-12 xl:col-span-6">
                            <h3>Montant des contrats par CCAG</h3>
                            <Graph :data="datas.fournitures?.montants" :layout />
                        </div>
                        <div class="col-span-12 xl:col-span-6">
                            <h3>Nombre de contrats par CCAG</h3>
                            <Graph :data="datas.fournitures?.nombres" :layout />
                        </div>
                    </div>
                </TabPanel>
            </TabPanels>
        </Tabs>
        <BoutonIframe v-if="acheteurSiret" :path="'acheteur/' + acheteurSiret + '/marches/ccag'" name="La répartition des marchés publics par clause administrative utilisée, sous forme de graphique" />
    </section>
</template>
