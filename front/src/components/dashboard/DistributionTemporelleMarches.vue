<script setup lang="ts">
import { getAcheteurUid } from '@/service/GetAcheteurService';
import { getMonthAsString, getNow } from '@/service/HelpersService';
import { computed, onMounted, ref, watch } from 'vue';

import { getListeMarches, type MarcheAllegeDto } from '@/client';
import type { PlotData } from 'plotly.js-dist';

const props = defineProps({
    acheteurUid: { type: [Number, null], default: null },
    acheteurSiret: { type: [String, null], default: null },
    vendeurUid: { type: [Number, null], default: null },
    dateMin: { type: Date, default: new Date(settings.date_min) },
    dateMax: { type: Date, default: getNow() },
    query: {
        type: Object,
        default: () => {
            return {};
        }
    }
});

const loading = ref(false);
const data = ref<Partial<PlotData>[]>();
const layout = computed(() => ({
    margin: { t: 0, r: 0, l: 60, b: 50 },
    xaxis: {
        type: 'date',
        range: [getMonthAsString(props.dateMin || new Date(settings.date_min)), getMonthAsString(props.dateMax || getNow())],
        title: { text: 'DATE' }
    },
    yaxis: { title: { text: 'MONTANT (€)' } }
}));

function transform(data: Array<MarcheAllegeDto>): Partial<PlotData>[] {
    const common_data = { mode: 'markers' as PlotData['mode'] };
    const common_marker = {
        line: {
            color: 'rgb(255, 255, 255)',
            width: 1
        },
        opacity: 0.7
    };
    const traces = [
        {
            x: [] as Date[],
            y: [] as number[],
            text: [] as string[],
            name: 'Travaux',
            marker: {
                size: 10,
                symbol: 'star-diamond',
                ...common_marker
            },
            ...common_data
        },
        {
            x: [] as Date[],
            y: [] as number[],
            text: [] as string[],
            name: 'Fournitures',
            marker: {
                size: 10,
                ...common_marker
            },
            ...common_data
        },
        {
            x: [] as Date[],
            y: [] as number[],
            text: [] as string[],
            name: 'Services',
            marker: {
                size: 10,
                symbol: 'square',
                ...common_marker
            },
            ...common_data
        }
    ];
    const keys = ['Travaux', 'Fournitures', 'Services'];
    for (var marche of data) {
        const key = keys.indexOf(marche.categorie);
        traces[key].x.push(marche.date_notification);
        traces[key].y.push(parseFloat(marche.montant));
        traces[key].text.push(marche.objet.substring(0, 100));
    }
    return traces;
}
async function fetchData() {
    loading.value = true;
    if (props.acheteurUid == -1) {
        return;
    }
    const acheteurUid = await getAcheteurUid(props.acheteurUid, props.acheteurSiret);
    getListeMarches({
        query: {
            date_debut: props.dateMin,
            date_fin: props.dateMax,
            acheteur_uid: acheteurUid,
            vendeur_uid: props.vendeurUid,
            ...props.query
        }
    }).then((response) => {
        if (response.data) {
            data.value = transform(response.data);
            loading.value = false;
        }
    });
}

watch([() => props.dateMin, () => props.dateMax, () => props.acheteurUid, () => props.vendeurUid, () => props.query], () => {
    fetchData();
});

onMounted(() => {
    fetchData();
});
</script>

<template>
    <section>
        <h2>Distribution temporelle des marchés</h2>
        <Graph :data :layout />
        <div v-if="loading" class="text-center">
            <ProgressSpinner style="width: 5rem; height: 5rem" />
        </div>
        <details>
            <summary>💡 Comment lire ce graphique ?</summary>
            <div class="flex flex-row gap-10">
                <div class="basis-1/2">
                    <p>Chaque point dans ce graphique représente un marché. Sa position horizontale indique la date dans laquelle il a été conclu. Sa position verticale, le montant du marché en euros.</p>
                    <p>La ligne pointillée en rouge indique la moyenne du montant des marchés affichés.</p>
                    <p>Veuillez noter que si la date d'un marché venait à manquer (par exemple, elle n'a pas été renseignée par l'acheteur), nous ne positionnerons pas le marché sur le graphique.</p>
                </div>

                <div class="basis-1/2">
                    <p>Pour faciliter l'interprétation, les marchés ont été divisés en 3 catégories que vous pouvez identifier par leur couleur :</p>
                    <ul>
                        <li>🟩 Vert pour les services</li>
                        <li>🔷 Bleu pour les travaux</li>
                        <li>🟠 Orange pour les fournitures</li>
                    </ul>
                </div>
            </div>
        </details>
        <BoutonIframe v-if="acheteurSiret" :path="'acheteur/' + acheteurSiret + '/marches/distribution'" name="La distribution des marchés dans le temps, sous forme de graphique" />
    </section>
</template>
