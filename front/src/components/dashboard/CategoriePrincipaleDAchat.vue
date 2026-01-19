<script setup lang="ts">
import { getCategories } from '@/client';
import { getAcheteurUid } from '@/service/GetAcheteurService';
import { bright_okabe_ito } from '@/service/GraphColorsService';
import { formatCurrency, formatNumber, getNow } from '@/service/HelpersService';
import { onMounted, ref, watch } from 'vue';

import type { CategoriesDto } from '@/client';
import type { Layout, PlotData } from 'plotly.js-dist';

const props = defineProps({
    acheteurUid: { type: [Number, null], default: null },
    acheteurSiret: { type: [String, null], default: null },
    vendeurUid: { type: [Number, null], default: null },
    dateMin: { type: [Date, null], default: null },
    dateMax: { type: [Date, null], default: null }
});

interface idatas {
    travaux: Partial<PlotData>[];
    services: Partial<PlotData>[];
    fournitures: Partial<PlotData>[];
}
const data = ref<Partial<idatas>>({});
const layout = {
    showlegend: false,
    margin: { t: 0, r: 0, b: 20 },
    xaxis: { type: 'date', range: [(props.dateMin ? props.dateMin : new Date(settings.date_min)).toISOString().substring(0, 10), (props.dateMax ? props.dateMax : getNow()).toISOString().substring(0, 10)] }
} as Partial<Layout>;

const stats = ref({
    montant_total: 0,
    nombre_total: 0,
    travaux: { montant_total: 0, nombre_total: 0 },
    fournitures: { montant_total: 0, nombre_total: 0 },
    services: { montant_total: 0, nombre_total: 0 }
});

function getNextMonth(date: string): string {
    let [year, month] = date.split('-').map((e) => parseInt(e));
    if (month == 12) {
        month = 1;
        year = year + 1;
    } else {
        month = month + 1;
    }
    return year + '-' + month;
}

function getPreviousMonth(date: string): string {
    let [year, month] = date.split('-').map((e) => parseInt(e));
    if (month == 1) {
        month = 12;
        year = year - 1;
    } else {
        month = month - 1;
    }
    return year + '-' + month.toString().padStart(2, '0');
}

function transform(input: CategoriesDto[]): idatas {
    const output = <idatas>{
        services: [{ x: [] as string[], y: [] as number[], type: 'scatter', mode: 'lines', fill: 'tozeroy', line: { color: bright_okabe_ito[3] }, fillcolor: bright_okabe_ito[3] }],
        travaux: [{ x: [], y: [], type: 'scatter', mode: 'lines', fill: 'tozeroy', line: { color: bright_okabe_ito[0] }, fillcolor: bright_okabe_ito[0] }],
        fournitures: [{ x: [], y: [], type: 'scatter', fill: 'tozeroy', mode: 'lines', line: { color: bright_okabe_ito[6] }, fillcolor: bright_okabe_ito[6] }]
    };
    const total_mensuel: { [month: string]: number } = {};

    stats.value = {
        montant_total: 0,
        nombre_total: 0,
        travaux: { montant_total: 0, nombre_total: 0 },
        fournitures: { montant_total: 0, nombre_total: 0 },
        services: { montant_total: 0, nombre_total: 0 }
    };

    // will be used to track gap between two values, and add 0 values to get a nice chart
    const previousByType = { services: null as null | CategoriesDto, travaux: null as null | CategoriesDto, fournitures: null as null | CategoriesDto, tout: null as null | CategoriesDto };

    for (let line of input) {
        const key = line.categorie.toLowerCase();

        const previousMonth = getPreviousMonth(line.mois);

        if (!previousByType[key] || previousByType[key].mois != previousMonth) {
            // set null value after previous line
            if (previousByType[key]) {
                output[key][0].y.push(0);
                output[key][0].x.push(getNextMonth(previousByType[key].mois));
            }

            // set null value before current line
            output[key][0].y.push(0);
            output[key][0].x.push(previousMonth);
        }

        if (!previousByType.tout || (previousByType.tout.mois != previousMonth && !total_mensuel[previousMonth])) {
            // set null value after previous line
            if (previousByType.tout) {
                total_mensuel[getNextMonth(previousByType.tout.mois)] = 0;
            }

            // set null value before current line
            total_mensuel[previousMonth] = 0;
        }

        output[key][0].y.push(parseFloat(line.montant));
        output[key][0].x.push(line.mois);

        if (line.mois in total_mensuel) {
            total_mensuel[line.mois] += parseFloat(line.montant);
        } else {
            total_mensuel[line.mois] = parseFloat(line.montant);
        }

        stats.value[key].montant_total += parseFloat(line.montant);
        stats.value[key].nombre_total += line.nombre;
        stats.value.montant_total += parseFloat(line.montant);
        stats.value.nombre_total += line.nombre;

        previousByType[key] = line;
        previousByType.tout = line;
    }

    // set lasts values for nice chart end
    for (let key of ['services', 'fournitures', 'travaux']) {
        if (previousByType[key]) {
            output[key][0].y.push(0);
            output[key][0].x.push(getNextMonth(previousByType[key].mois));
        }
    }
    if (previousByType.tout) {
        total_mensuel[getNextMonth(previousByType.tout.mois)] = 0;
    }

    const total = <Partial<PlotData>>{
        type: 'scatter',
        mode: 'lines',
        fill: 'tozeroy',
        fillcolor: '#dadada',
        line: { color: '#ccc' },
        x: [],
        y: []
    };

    total.x = Object.keys(total_mensuel);
    total.y = Object.values(total_mensuel);

    output.services.unshift(total);
    output.travaux.unshift(total);
    output.fournitures.unshift(total);

    return output;
}

async function fetchData() {
    const acheteurUid = await getAcheteurUid(props.acheteurUid, props.acheteurSiret);
    if (acheteurUid || props.vendeurUid || !props.acheteurSiret) {
        getCategories({
            query: {
                date_debut: props.dateMin,
                date_fin: props.dateMax,
                acheteur_uid: acheteurUid,
                vendeur_uid: props.vendeurUid
            }
        }).then((response) => {
            if (response.data) {
                data.value = transform(response.data);
            }
        });
    }
}

onMounted(() => {
    fetchData();
});

watch([() => props.dateMin, () => props.dateMax, () => props.acheteurUid, () => props.vendeurUid], () => {
    fetchData();
});
</script>

<template>
    <section class="grid grid-cols-12 gap-8">
        <div class="col-span-12">
            <h2 class="title">Distribution par catégorie principale d'achat</h2>
            <p>Comparaison des trois catégories d'achats (zone colorée) par rapport au total (zone grise).</p>
        </div>
        <div class="col-span-12 xl:col-span-4">
            <h3>Services</h3>
            <Graph :data="data.services" :layout />
            <div class="grid grid-cols-3 gap-1 text-center">
                <div class="label">Nombre</div>
                <div class="categorie">{{ formatNumber(stats.services.nombre_total) }}</div>
                <div class="total">{{ formatNumber(stats.nombre_total) }} marchés</div>
                <div class="label">Montant</div>
                <div class="categorie">{{ formatCurrency(stats.services.montant_total) }}</div>
                <div class="total">{{ formatCurrency(stats.montant_total) }}</div>
            </div>
        </div>
        <div class="col-span-12 xl:col-span-4">
            <h3>Travaux</h3>
            <Graph :data="data.travaux" :layout />
            <div class="grid grid-cols-3 gap-1 text-center">
                <div class="label">Nombre</div>
                <div class="categorie">{{ formatNumber(stats.travaux.nombre_total) }}</div>
                <div class="total">{{ formatNumber(stats.nombre_total) }} marchés</div>
                <div class="label">Montant</div>
                <div class="categorie">{{ formatCurrency(stats.travaux.montant_total) }}</div>
                <div class="total">{{ formatCurrency(stats.montant_total) }}</div>
            </div>
        </div>
        <div class="col-span-12 xl:col-span-4">
            <h3>Fournitures</h3>
            <Graph :data="data.fournitures" :layout />
            <div class="grid grid-cols-3 gap-1 text-center">
                <div class="label">Nombre</div>
                <div class="categorie">{{ formatNumber(stats.fournitures.nombre_total) }}</div>
                <div class="total">{{ formatNumber(stats.nombre_total) }} marchés</div>
                <div class="label">Montant</div>
                <div class="categorie">{{ formatCurrency(stats.fournitures.montant_total) }}</div>
                <div class="total">{{ formatCurrency(stats.montant_total) }}</div>
            </div>
        </div>
        <div class="col-span-12">
            <BoutonIframe v-if="props.acheteurSiret" :acheteurSiret="props.acheteurSiret" path="categorie-marches" name="La répartition des marchés publics par catégorie, sous forme de graphique" />
        </div>
    </section>
</template>

<style scoped>
.label {
    text-align: right;
    text-transform: uppercase;
    color: var(--p-primary-color);
    font-weight: bold;
}

.categorie {
    color: var(--p-primary-color);
    font-weight: bold;
}

.total {
    font-size: 0.9rem;
}
</style>
