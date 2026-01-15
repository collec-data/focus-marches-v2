<script setup lang="ts">
import { getConsiderations, getConsiderationsEnvEtSociale, getConsiderationsEnvironnementale, getConsiderationsSociale } from '@/client';
import { okabe_ito } from '@/service/GraphColorsService';
import { breakLongLabel } from '@/service/HelpersService';
import { onMounted, ref, watch } from 'vue';

import type { ConsiderationDto, ConsiderationsEnvDto, ConsiderationsSocialeDto } from '@/client';
import type { PlotData } from 'plotly.js-dist';

const props = defineProps({
    acheteurUid: { type: [Number, null], default: null },
    vendeurUid: { type: [Number, null], default: null },
    dateMin: { type: Date, required: true },
    dateMax: { type: Date, required: true }
});

interface dataInterface {
    values: Array<number>;
    labels: Array<string>;
}

function makeCamembert(data: dataInterface): Partial<PlotData>[] {
    return [
        {
            values: data.values,
            labels: data.labels,
            type: 'pie',
            marker: {
                colors: okabe_ito
            }
        }
    ];
}

function transform(input: Array<ConsiderationsEnvDto | ConsiderationsSocialeDto | ConsiderationDto>): dataInterface {
    const output: dataInterface = { values: [], labels: [] };
    for (let line of input) {
        output.values.push(line.nombre);
        output.labels.push(breakLongLabel(line.consideration, 16));
    }
    return output;
}

const dataAnnuel = ref<Partial<PlotData>[]>([]);
const layoutAnnuel = { barmode: 'stack', margin: { t: 0, l: 0 } };

const dataGlobal = ref<Partial<PlotData>[]>([]);
const dataEnv = ref<Partial<PlotData>[]>([]);
const dataSocial = ref<Partial<PlotData>[]>([]);
const dataSocialEnv = ref<Partial<PlotData>[]>([]);

function fetchData() {
    const y2024 = new Date(Date.UTC(2024, 1, 1));
    const query = {
        date_debut: props.dateMin > y2024 ? props.dateMin : y2024,
        date_fin: props.dateMax,
        acheteur_uid: props.acheteurUid,
        vendeur_uid: props.vendeurUid
    };
    getConsiderationsEnvironnementale({ query: query }).then((response) => {
        if (response.data) {
            dataEnv.value = makeCamembert(transform(response.data));
        }
    });
    getConsiderationsSociale({ query: query }).then((response) => {
        if (response.data) {
            dataSocial.value = makeCamembert(transform(response.data));
        }
    });
    getConsiderations({ query: query }).then((response) => {
        if (response.data) {
            const totaux: dataInterface = { values: [], labels: [] };
            dataAnnuel.value = (() => {
                const result = [] as Partial<PlotData>[];
                for (let [k, e] of response.data.entries()) {
                    let initialValue = 0;
                    totaux.labels.push(breakLongLabel(e.consideration, 16));
                    totaux.values.push(e.data.reduce((accumulator, currentValue) => accumulator + currentValue.nombre, initialValue));
                    result.push({ x: e.data.map((d) => d.annee), y: e.data.map((d) => d.nombre), name: breakLongLabel(e.consideration, 16), type: 'bar', marker: { color: okabe_ito[k], line: { color: okabe_ito[k], width: 1 } } });
                }
                return result;
            })();
            dataGlobal.value = makeCamembert(totaux);
        }
    });
    getConsiderationsEnvEtSociale({ query: query }).then((response) => {
        if (response.data) {
            dataSocialEnv.value = makeCamembert(transform(response.data));
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
    <section>
        <h2>L'achat durable</h2>
        <p>Les données sur les considération environnementales et sociales ne sont communiquées qu'à partir du 01/01/2024, date à laquelle elles ont été rendues obligatoires.</p>
        <div class="grid grid-cols-12 gap-8">
            <div class="col-span-12 xl:col-span-6">
                <h3>Répartition globale par nombre de marchés</h3>
                <Graph :data="dataGlobal" />
            </div>
            <div class="col-span-12 xl:col-span-6">
                <h3>Evolution dans le temps</h3>
                <p>(Prise en compte de la date de notification)</p>
                <Graph :data="dataAnnuel" :layout="layoutAnnuel" />
            </div>
        </div>
        <div class="grid grid-cols-12 gap-8">
            <div class="col-span-12 xl:col-span-4">
                <h3>Nombre de marchés à considérations uniquement environnementales</h3>
                <Graph :data="dataEnv" />
            </div>
            <div class="col-span-12 xl:col-span-4">
                <h3>Nombre de marchés à considérations uniquement sociales</h3>
                <Graph :data="dataSocial" />
            </div>
            <div class="col-span-12 xl:col-span-4">
                <h3>Nombre de marchés à considérations environnementales et sociales</h3>
                <Graph :data="dataSocialEnv" />
            </div>
        </div>
    </section>
</template>
