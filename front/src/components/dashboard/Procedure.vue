<script setup lang="ts">
import { getMarchesParProcedure } from '@/client';
import { okabe_ito } from '@/service/GraphColorsService';
import { getDurationInMonths, getNow, longLabelsBreaker } from '@/service/HelpersService';
import { useStructureIdentifiee } from '@/service/UseStructureIdentifiee';
import { useReactiveFetch } from '@/utils/query';
import { computed } from 'vue';
import Graph from '../Graph.vue';

import type { MarcheProcedureDto } from '@/client';
import type { Layout, PlotData } from 'plotly.js-dist';
import type { PropType } from 'vue';

// Pas de valeur par défaut : `undefined` signifie « acheteur encore non identifié », `null` « aucun acheteur demandé ».
const props = defineProps({
    acheteurUid: { type: Number as PropType<number | null>, required: false },
    acheteurSiret: { type: String as PropType<string | null>, required: false },
    vendeurUid: { type: Number as PropType<number | null>, required: false },
    dateMin: { type: Date, required: false, default: new Date(settings.date_min) },
    dateMax: { type: Date, required: false, default: getNow() }
});

const layout = { margin: { l: 130, t: 0, b: 20, r: 0 } } as Layout;

function transform(input: Array<MarcheProcedureDto>) {
    let output = {
        procedure: [] as Array<string | null>,
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

function makeGraph(labels: Array<string | null>, data: Array<number>): Partial<PlotData>[] {
    return [
        {
            y: longLabelsBreaker(labels),
            x: data,
            type: 'bar',
            orientation: 'h',
            marker: { color: okabe_ito, line: { color: okabe_ito, width: 1 } }
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

const { etat, refetch } = useReactiveFetch(getMarchesParProcedure, options);

// On ne dessine rien avant la réponse : un graphique à zéro barre laisserait croire à une absence de contrats.
const montantData = computed(() => {
    if (etat.value.statut !== 'succes') {
        return undefined;
    }
    const brut = transform(etat.value.data);
    return makeGraph(brut.procedure, brut.montant);
});

const nombreData = computed(() => {
    if (etat.value.statut !== 'succes') {
        return undefined;
    }
    const brut = transform(etat.value.data);
    return makeGraph(brut.procedure, brut.nombre);
});
</script>

<template>
    <Fluid class="grid grid-cols-12 gap-8">
        <div class="col-span-12">
            <h2 class="title">Procédure suivie</h2>
            <p class="subtitle">Classement des contrats selon la procédure suivie lors de la consultation. La période observée est de {{ getDurationInMonths(dateMin, dateMax) }} mois</p>
        </div>

        <ErreurChargement v-if="erreurAcheteur" :erreur="erreurAcheteur" message="Aucune structure ne correspond à ce SIRET" class="col-span-12" @retry="refetchAcheteur" />
        <ErreurChargement v-else-if="etat.statut === 'erreur'" :erreur="etat.erreur" message="Le chargement de la répartition par procédure a échoué" class="col-span-12" @retry="refetch" />
        <ChargementEnCours v-else-if="etat.statut !== 'succes'" class="col-span-12" libelle="Chargement de la répartition par procédure" />

        <template v-else>
            <div class="col-span-12 xl:col-span-6">
                <h3>Montant des contrats par procédure</h3>
                <Graph :data="montantData" :layout title="Montant des contrats par procédure" />
            </div>
            <div class="col-span-12 xl:col-span-6">
                <h3>Nombre des contrats par procédure</h3>
                <Graph :data="nombreData" :layout title="Nombre de contrats par procédure" />
            </div>
        </template>

        <div class="col-span-12">
            <BoutonIframe v-if="acheteurSiret" :path="'acheteur/' + acheteurSiret + '/marches/procedure'" name="La répartition des marchés publics par procédure suivie, sous forme de graphique" />
        </div>
    </Fluid>
</template>
