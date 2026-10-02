<script setup lang="ts">
import { getMarchesParNature } from '@/client';
import { okabe_ito } from '@/service/GraphColorsService';
import { formatCurrency, getDurationInMonths, getMonthAsString, getNow } from '@/service/HelpersService';
import { useStructureIdentifiee } from '@/service/UseStructureIdentifiee';
import { useReactiveFetch } from '@/utils/query';
import { computed } from 'vue';

import type { MarcheNatureDto } from '@/client';
import type { PropType } from 'vue';
import type Plotly from 'plotly.js-dist';

// Pas de valeur par défaut : `undefined` signifie « acheteur encore non identifié », `null` « aucun acheteur demandé ».
const props = defineProps({
    acheteurUid: { type: Number as PropType<number | null>, required: false },
    acheteurSiret: { type: String as PropType<string | null>, required: false },
    vendeurUid: { type: Number as PropType<number | null>, required: false },
    dateMin: { type: Date, required: false, default: new Date(settings.date_min) },
    dateMax: { type: Date, required: false, default: getNow() }
});

interface StatNature {
    montant_total: number;
    nombre_total: number;
}

function transform(input: Array<MarcheNatureDto>) {
    const output = [
        { labels: [] as Array<string>, values: [] as Array<number> },
        { labels: [] as Array<string>, values: [] as Array<number> },
        { labels: [] as Array<string>, values: [] as Array<number> }
    ];
    const cumul: Array<StatNature> = [
        { montant_total: 0, nombre_total: 0 },
        { montant_total: 0, nombre_total: 0 },
        { montant_total: 0, nombre_total: 0 }
    ];

    for (let line of input) {
        // les valeurs de `line.nature` vont de 1 à 3 -> on décale
        // pour se caler sur les tableaux dont les indices commencent à 0
        output[line.nature - 1].labels.push(line.mois);
        output[line.nature - 1].values.push(parseFloat(line.montant));
        cumul[line.nature - 1].montant_total += parseFloat(line.montant);
        cumul[line.nature - 1].nombre_total += line.nombre;
    }
    return { series: output, cumul };
}

const layout = computed(() => ({
    margin: { t: 0, r: 0, b: 20 },
    xaxis: { type: 'date', range: [getMonthAsString(props.dateMin || new Date(settings.date_min)), getMonthAsString(props.dateMax || getNow())] }
}));
const config = { displayModeBar: false } as Partial<Plotly.Config>;

function makeGraph(labels: Array<string | null>, data: Array<number>, color: string): Array<Partial<Plotly.PlotData>> {
    return [
        {
            x: labels,
            y: data,
            type: 'bar',
            marker: { color: color, line: { color: color, width: 1 } }
        }
    ];
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

const { etat, refetch } = useReactiveFetch(getMarchesParNature, options);

// Aucun cumul ni graphique avant la réponse : trois zéros présentés comme des totaux seraient une fausse mesure.
const brut = computed(() => (etat.value.statut === 'succes' ? transform(etat.value.data) : null));

const cumul = computed<Array<StatNature> | null>(() => brut.value?.cumul ?? null);

function graphique(index: number): Partial<Plotly.PlotData>[] | undefined {
    if (brut.value === null) {
        return undefined;
    }
    const serie = brut.value.series[index];
    return makeGraph(serie.labels, serie.values, okabe_ito[index]);
}

const marcheData = computed(() => graphique(0));
const partenariatData = computed(() => graphique(1));
const defenseData = computed(() => graphique(2));
</script>

<template>
    <section class="flex flex-col">
        <h2 class="title">Nature des contrats</h2>
        <p>Répartition des contrats par nature du marché public, en montant et en nombre. La période observée est de {{ getDurationInMonths(dateMin, dateMax) }} mois et les marchés sont groupés par mois.</p>

        <ErreurChargement v-if="erreurAcheteur" :erreur="erreurAcheteur" message="Aucune structure ne correspond à ce SIRET" @retry="refetchAcheteur" />
        <ErreurChargement v-else-if="etat.statut === 'erreur'" :erreur="etat.erreur" message="Le chargement de la répartition par nature a échoué" @retry="refetch" />
        <ChargementEnCours v-else-if="!cumul" libelle="Chargement de la répartition par nature" />

        <div v-else class="flex flex-row gap-5 flex-wrap">
            <div class="nature basis-md grow shrink">
                <h3>Marché</h3>
                <Graph :data="marcheData" :layout :config title="Répartition des contrats de type marchés" />
                <ul>
                    <li><span>Montant</span> {{ formatCurrency(cumul[0].montant_total) }}</li>
                    <li><span>Nombre</span> {{ cumul[0].nombre_total }} marchés</li>
                </ul>
            </div>
            <div class="nature basis-md grow shrink">
                <h3>Marché de partenariat</h3>
                <Graph :data="partenariatData" :layout :config title="Répartition des contrats de type marchés de partenariats" />
                <ul>
                    <li><span>Montant</span> {{ formatCurrency(cumul[1].montant_total) }}</li>
                    <li><span>Nombre</span> {{ cumul[1].nombre_total }} marchés</li>
                </ul>
            </div>
            <div class="nature basis-md grow shrink">
                <h3>Marché de défense ou de sécurité</h3>
                <Graph :data="defenseData" :layout :config title="Répartition des contrats de type marchés de défense ou de sécurité" />
                <ul>
                    <li><span>Montant</span> {{ formatCurrency(cumul[2].montant_total) }}</li>
                    <li><span>Nombre</span> {{ cumul[2].nombre_total }} marchés</li>
                </ul>
            </div>
        </div>
        <details>
            <summary>💡 Comment lire ces graphiques ?</summary>
            <div class="flex flex-row gap-10">
                <div class="basis-1/2">
                    <h3>Comment lire ces graphiques ?</h3>
                    <p>Les marchés publics sont répartis en quatre grandes natures de contrats :</p>
                    <ul>
                        <li>Marché : cas général, contrat entre un acheteur public et un fournisseur</li>
                        <li>Marché de partenariat : contrat spécifique qui « permet de confier à un opérateur économique ou à un groupement d’opérateurs économiques une mission globale » sous maîtrise d’ouvrage privée.</li>
                        <li>Marché de défense ou de sécurité :</li>
                    </ul>
                </div>

                <div class="basis-1/2">
                    <h3>Pour chaque catégorie il est indiqué :</h3>
                    <p>Le montant total, le nombre de contrats, un affichage de leur distribution temporelle. La hauteur des barres (axe Y) reflète le montant.</p>
                    <p>Vous pouvez survoler les graphiques avec votre souris pour plus d’informations.</p>
                </div>
            </div>
        </details>
        <BoutonIframe v-if="acheteurSiret" :path="'acheteur/' + acheteurSiret + '/marches/nature'" name="La répartition des marchés publics par nature, sous forme de graphique" />
    </section>
</template>

<style scoped>
.nature h3 {
    margin: 0;
}

.nature .chart {
    aspect-ratio: 4/3;
    width: 100%;
}

.nature ul span {
    display: inline-block;
    width: 50%;
    text-align: right;
    padding-right: 2rem;
    text-transform: uppercase;
    color: var(--p-primary-color);
    font-weight: bold;
}
</style>
