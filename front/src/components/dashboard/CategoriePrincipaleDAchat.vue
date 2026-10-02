<script setup lang="ts">
import { getCategories } from '@/client';
import { bright_okabe_ito } from '@/service/GraphColorsService';
import { formatCurrency, formatNumber, getMonthAsString, getNow } from '@/service/HelpersService';
import { useStructureIdentifiee } from '@/service/UseStructureIdentifiee';
import { useReactiveFetch } from '@/utils/query';
import { computed } from 'vue';

import type { CategoriesDto } from '@/client';
import type { PropType } from 'vue';
import type { PlotData } from 'plotly.js-dist';

// Pas de valeur par défaut : `undefined` signifie « acheteur encore non identifié », `null` « aucun acheteur demandé ».
const props = defineProps({
    acheteurUid: { type: Number as PropType<number | null>, required: false },
    acheteurSiret: { type: String as PropType<string | null>, required: false },
    vendeurUid: { type: Number as PropType<number | null>, required: false },
    dateMin: { type: Date as PropType<Date | null>, required: false },
    dateMax: { type: Date as PropType<Date | null>, required: false }
});

interface idatas {
    travaux: Partial<PlotData>[];
    services: Partial<PlotData>[];
    fournitures: Partial<PlotData>[];
}
const layout = computed(() => ({
    showlegend: false,
    margin: { t: 0, r: 0, b: 20 },
    xaxis: { type: 'date', range: [getMonthAsString(props.dateMin || new Date(settings.date_min)), getMonthAsString(props.dateMax || getNow())] }
}));

interface StatCategorie {
    montant_total: number;
    nombre_total: number;
}
type Stats = StatCategorie & { travaux: StatCategorie; fournitures: StatCategorie; services: StatCategorie };

const statsVides = (): Stats => ({
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

function transform(input: CategoriesDto[]): { series: idatas; stats: Stats } {
    const output = <idatas>{
        services: [{ x: [] as string[], y: [] as number[], type: 'scatter', mode: 'lines', fill: 'tozeroy', line: { color: bright_okabe_ito[3] }, fillcolor: bright_okabe_ito[3] }],
        travaux: [{ x: [], y: [], type: 'scatter', mode: 'lines', fill: 'tozeroy', line: { color: bright_okabe_ito[0] }, fillcolor: bright_okabe_ito[0] }],
        fournitures: [{ x: [], y: [], type: 'scatter', fill: 'tozeroy', mode: 'lines', line: { color: bright_okabe_ito[6] }, fillcolor: bright_okabe_ito[6] }]
    };
    const total_mensuel: { [month: string]: number } = {};

    const stats = statsVides();

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

        stats[key].montant_total += parseFloat(line.montant);
        stats[key].nombre_total += line.nombre;
        stats.montant_total += parseFloat(line.montant);
        stats.nombre_total += line.nombre;

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

    return { series: output, stats };
}

const {
    uid,
    erreur: erreurAcheteur,
    refetch: refetchAcheteur
} = useStructureIdentifiee(
    () => props.acheteurUid,
    () => props.acheteurSiret
);

const options = computed(() => {
    if (uid.value === undefined) {
        return undefined;
    }
    return {
        query: {
            date_debut: props.dateMin ?? undefined,
            date_fin: props.dateMax ?? undefined,
            acheteur_uid: uid.value ?? undefined,
            vendeur_uid: props.vendeurUid ?? undefined
        }
    };
});

const { etat, refetch } = useReactiveFetch(getCategories, options);

// Aucun cumul ni graphique avant la réponse : des totaux à zéro seraient une fausse mesure.
const brut = computed(() => (etat.value.statut === 'succes' ? transform(etat.value.data) : null));

const data = computed<Partial<idatas>>(() => brut.value?.series ?? {});
const stats = computed<Stats | null>(() => brut.value?.stats ?? null);
</script>

<template>
    <section class="grid grid-cols-12 gap-8">
        <div class="col-span-12">
            <h2 class="title">Distribution par catégorie principale d'achat</h2>
            <p>Comparaison des trois catégories d'achats (zone colorée) par rapport au total (zone grise).</p>
        </div>

        <ErreurChargement v-if="erreurAcheteur" :erreur="erreurAcheteur" message="Aucune structure ne correspond à ce SIRET" class="col-span-12" @retry="refetchAcheteur" />
        <ErreurChargement v-else-if="etat.statut === 'erreur'" :erreur="etat.erreur" message="Le chargement de la répartition par catégorie a échoué" class="col-span-12" @retry="refetch" />
        <ChargementEnCours v-else-if="!stats" class="col-span-12" libelle="Chargement de la répartition par catégorie" />

        <template v-else>
            <div class="col-span-12 xl:col-span-4">
                <h3>Services</h3>
                <Graph :data="data.services" :layout title="Distribution temporelle des marchés de services" />
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
                <Graph :data="data.travaux" :layout title="Distribution temporelle des marchés de travaux" />
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
                <Graph :data="data.fournitures" :layout title="Distribution temporelle des marchés de fournitures" />
                <div class="grid grid-cols-3 gap-1 text-center">
                    <div class="label">Nombre</div>
                    <div class="categorie">{{ formatNumber(stats.fournitures.nombre_total) }}</div>
                    <div class="total">{{ formatNumber(stats.nombre_total) }} marchés</div>
                    <div class="label">Montant</div>
                    <div class="categorie">{{ formatCurrency(stats.fournitures.montant_total) }}</div>
                    <div class="total">{{ formatCurrency(stats.montant_total) }}</div>
                </div>
            </div>
        </template>

        <div class="col-span-12">
            <BoutonIframe v-if="acheteurSiret" :path="'acheteur/' + acheteurSiret + '/marches/categorie'" name="La répartition des marchés publics par catégorie, sous forme de graphique" />
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
