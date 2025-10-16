<script setup lang="ts">
import { getListeMarchesMarcheGet } from '@/client';
import { formatDate } from '@/service/HelpersService';
import { onMounted, ref, watch } from 'vue';

import type { MarcheAllegeDtoOutput } from '@/client';
import type { PlotData } from 'plotly.js-dist';

const props = defineProps({
    acheteurUid: { type: [String, null], default: null },
    vendeurUid: { type: [String, null], default: null },
    dateMin: { type: [Date, null], default: null },
    dateMax: { type: [Date, null], default: null }
});

const data = ref<Partial<PlotData>[]>();
const layout = { margin: { t: 0, r: 0, l: 20, b: 50 }, xaxis: { dtick: 24 } };

function transform(data: Array<MarcheAllegeDtoOutput>): Partial<PlotData>[] {
    const x = [] as string[];
    const y = [] as number[];
    const text = [] as string[];
    for (var marche of data) {
        x.push(formatDate(marche.date_notification));
        y.push(parseFloat(marche.montant));
        text.push(marche.objet.substring(0, 100));
    }
    return [
        {
            x: x,
            y: y,
            text: text,
            mode: 'markers',
            type: 'scatter',
            name: 'Marchés',
            marker: { size: 5 }
        }
    ];
}
function fetchData() {
    getListeMarchesMarcheGet({
        query: {
            date_debut: props.dateMin,
            date_fin: props.dateMax,
            acheteur_uid: props.acheteurUid
        }
    }).then((response) => {
        if (response.data) {
            data.value = transform(response.data);
        }
    });
}

watch([() => props.dateMin, () => props.dateMax, () => props.acheteurUid, () => props.vendeurUid], () => {
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
                        <li>🟢 Vert pour les services</li>
                        <li>🔵 Bleu pour les travaux</li>
                        <li>🟠 Orange pour les fournitures</li>
                    </ul>
                </div>
            </div>
        </details>
    </section>
</template>
