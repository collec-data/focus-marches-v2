<script setup lang="ts">
import { getCategories } from '@/client';
import { getAcheteurUid } from '@/service/GetAcheteurService';
import { bright_okabe_ito } from '@/service/GraphColorsService';
import { formatCurrency, formatNumber } from '@/service/HelpersService';
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
const layout = { showlegend: false, margin: { t: 0, r: 0, b: 20 }, xaxis: { type: 'date' } } as Partial<Layout>;

const stats = ref({
    montant_total: 0,
    nombre_total: 0,
    travaux: { montant_total: 0, nombre_total: 0 },
    fournitures: { montant_total: 0, nombre_total: 0 },
    services: { montant_total: 0, nombre_total: 0 }
});

function transform(input: CategoriesDto[]): idatas {
    const output = <idatas>{
        services: [{ x: [], y: [], type: 'scatter', mode: 'lines', fill: 'tozeroy', line: { color: bright_okabe_ito[3] }, fillcolor: bright_okabe_ito[3] }],
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

    for (let line of input) {
        const key = line.categorie.toLowerCase();

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
