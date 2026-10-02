<script setup lang="ts">
import { getConsiderations, getConsiderationsEnvEtSociale, getConsiderationsEnvironnementale, getConsiderationsSociale } from '@/client';
import { okabe_ito } from '@/service/GraphColorsService';
import { breakLongLabel, getMonthAsString, getNow } from '@/service/HelpersService';
import { useStructureIdentifiee } from '@/service/UseStructureIdentifiee';
import { useReactiveFetch } from '@/utils/query';
import type { ErreurReactiveFetch } from '@/utils/query';
import { computed } from 'vue';

import type { ConsiderationDto, ConsiderationsEnvDto, ConsiderationsSocialeDto } from '@/client';
import type { PropType } from 'vue';
import type { PlotData } from 'plotly.js-dist';

// Pas de valeur par défaut : `undefined` signifie « acheteur encore non identifié », `null` « aucun acheteur demandé ».
const props = defineProps({
    acheteurUid: { type: Number as PropType<number | null>, required: false },
    acheteurSiret: { type: String as PropType<string | null>, required: false },
    vendeurUid: { type: Number as PropType<number | null>, required: false },
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

const layoutAnnuel = computed(() => ({
    barmode: 'stack',
    margin: { t: 0, l: 0 },
    xaxis: { type: 'date', range: [getMonthAsString(props.dateMin || new Date(settings.date_min)), getMonthAsString(props.dateMax || getNow())] }
}));

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
    // Les considérations ne sont communiquées qu'à partir du 01/01/2024.
    const debutObligation = new Date(Date.UTC(2024, 1, 1));
    return {
        query: {
            date_debut: props.dateMin > debutObligation ? props.dateMin : debutObligation,
            date_fin: props.dateMax,
            acheteur_uid: uid.value ?? undefined,
            vendeur_uid: props.vendeurUid ?? undefined
        }
    };
});

// Quatre agrégats distincts, tous assujettis à la même identité : aucun ne part avant qu'elle soit résolue.
const environnement = useReactiveFetch(getConsiderationsEnvironnementale, options);
const sociale = useReactiveFetch(getConsiderationsSociale, options);
const annuel = useReactiveFetch(getConsiderations, options);
const socialEnv = useReactiveFetch(getConsiderationsEnvEtSociale, options);

const requetes = [environnement, sociale, annuel, socialEnv];

// L'écran n'a de sens qu'une fois les quatre réponses reçues : le premier échec suffit à le signaler.
const reussite = computed(() => requetes.every((requete) => requete.etat.value.statut === 'succes'));
const premiereErreur = computed<ErreurReactiveFetch | null>(() => {
    for (const requete of requetes) {
        if (requete.etat.value.statut === 'erreur') {
            return requete.etat.value.erreur;
        }
    }
    return null;
});

function camembert(donnees: Array<ConsiderationsEnvDto | ConsiderationsSocialeDto | ConsiderationDto>): Partial<PlotData>[] {
    return makeCamembert(transform(donnees));
}

const dataEnv = computed(() => (environnement.etat.value.statut === 'succes' ? camembert(environnement.etat.value.data) : []));
const dataSocial = computed(() => (sociale.etat.value.statut === 'succes' ? camembert(sociale.etat.value.data) : []));
const dataSocialEnv = computed(() => (socialEnv.etat.value.statut === 'succes' ? camembert(socialEnv.etat.value.data) : []));

const dataAnnuel = computed<Partial<PlotData>[]>(() => {
    if (annuel.etat.value.statut !== 'succes') {
        return [];
    }
    const totaux: dataInterface = { values: [], labels: [] };
    const result = [] as Partial<PlotData>[];
    for (let [k, e] of annuel.etat.value.data.entries()) {
        totaux.labels.push(breakLongLabel(e.consideration, 16));
        totaux.values.push(e.data.reduce((accumulator, currentValue) => accumulator + currentValue.nombre, 0));
        result.push({ x: e.data.map((d) => d.annee), y: e.data.map((d) => d.nombre), name: breakLongLabel(e.consideration, 16), type: 'bar', marker: { color: okabe_ito[k], line: { color: okabe_ito[k], width: 1 } } });
    }
    return result;
});

const dataGlobal = computed<Partial<PlotData>[]>(() => {
    if (annuel.etat.value.statut !== 'succes') {
        return [];
    }
    const totaux: dataInterface = { values: [], labels: [] };
    for (const e of annuel.etat.value.data) {
        totaux.labels.push(breakLongLabel(e.consideration, 16));
        totaux.values.push(e.data.reduce((accumulator, currentValue) => accumulator + currentValue.nombre, 0));
    }
    return makeCamembert(totaux);
});
</script>

<template>
    <section>
        <h2>L'achat durable</h2>
        <p>Les données sur les considération environnementales et sociales ne sont communiquées qu'à partir du 01/01/2024, date à laquelle elles ont été rendues obligatoires.</p>

        <ErreurChargement v-if="erreurAcheteur" :erreur="erreurAcheteur" message="Aucune structure ne correspond à ce SIRET" @retry="refetchAcheteur" />
        <ErreurChargement v-else-if="premiereErreur" :erreur="premiereErreur" message="Le chargement des données d'achat durable a échoué" @retry="() => requetes.forEach((requete) => requete.refetch())" />
        <ChargementEnCours v-else-if="!reussite" libelle="Chargement des données d'achat durable" />

        <div v-else class="grid grid-cols-12 gap-8">
            <div class="col-span-12 xl:col-span-6">
                <h3>Répartition globale par nombre de marchés</h3>
                <Graph :data="dataGlobal" title="Répartition globale des considérations sociales en environnementales par nombre de marchés" />
            </div>
            <div class="col-span-12 xl:col-span-6">
                <h3>Evolution dans le temps</h3>
                <p>(Prise en compte de la date de notification)</p>
                <Graph :data="dataAnnuel" :layout="layoutAnnuel" title="Evolution dans le temps des considérations sociales et environnementales" />
            </div>
        </div>
        <div class="grid grid-cols-12 gap-8">
            <div class="col-span-12 xl:col-span-4">
                <h3>Nombre de marchés à considérations uniquement environnementales</h3>
                <Graph :data="dataEnv" title="Nombre de marchés à considérations uniquement environnementales" />
            </div>
            <div class="col-span-12 xl:col-span-4">
                <h3>Nombre de marchés à considérations uniquement sociales</h3>
                <Graph :data="dataSocial" title="Nombre de marchés à considérations uniquement sociales" />
            </div>
            <div class="col-span-12 xl:col-span-4">
                <h3>Nombre de marchés à considérations environnementales et sociales</h3>
                <Graph :data="dataSocialEnv" title="Nombre de marchés à considérations environnementales et sociales" />
            </div>
        </div>
        <BoutonIframe v-if="acheteurSiret" :path="'acheteur/' + acheteurSiret + '/marches/achat-durable'" name="La répartition des marchés publics par nature, sous forme de graphique" />
    </section>
</template>
