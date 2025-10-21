<script setup lang="ts">
import { listAcheteursStructureAcheteurGet, listVendeursStructureVendeurGet } from '@/client';
import { okabe_ito } from '@/service/GraphColorsService';
import { formatCurrency, structureName } from '@/service/HelpersService';
import { onMounted, ref } from 'vue';

import type { StructureAggMarchesDto } from '@/client';
import type { Layout, PlotData } from 'plotly.js-dist';

const props = defineProps({
    type: String,
    acheteurUid: { type: [String, null], default: null },
    vendeurUid: { type: [String, null], default: null },
    dateMin: { type: [Date, null], default: null },
    dateMax: { type: [Date, null], default: null }
});

const listeStructures = ref<Array<StructureAggMarchesDto>>([]);

let title = '';
let description = '';
let btn_label = '';

if (props.type == 'acheteurs') {
    title = 'Qui achète ?';
    description = 'Top 12 des acheteurs classés par montant total des contrats conclus au cours des 56 derniers mois. Survolez les noms les acheteurs pour les afficher en entier.';
    btn_label = 'Liste complète des organismes acheteurs';
} else {
    title = 'Qui réalise ?';
    description = 'Top 12 des fournisseurs classés par montant total des contrats remportés au cours des 56 derniers mois. Survolez les noms des fournisseurs pour les afficher en entier.';
    btn_label = 'Liste complète des fournisseurs';
}

const data = ref<Partial<PlotData>[]>();
const layout = { margin: { t: 0 } } as Partial<Layout>;

function transform(input: Array<StructureAggMarchesDto>) {
    let output = {
        structures: [] as Array<string | null>,
        montants: [] as Array<string>
    };
    for (var line of input) {
        output.structures.push(structureName(line.structure));
        output.montants.push(line.montant);
    }
    return output;
}

onMounted(() => {
    (props.type == 'acheteurs' ? listAcheteursStructureAcheteurGet : listVendeursStructureVendeurGet)({
        query: {
            limit: 12,
            acheteur_uid: props.acheteurUid ? parseInt(props.acheteurUid) : null,
            vendeur_uid: props.vendeurUid ? parseInt(props.vendeurUid) : null,
            date_debut: props.dateMin,
            date_fin: props.dateMax
        }
    }).then((response) => {
        if (response.data) {
            listeStructures.value = response.data;
            let rawData = transform(response.data);
            data.value = [
                {
                    x: rawData.structures,
                    y: rawData.montants,
                    type: 'bar',
                    marker: { color: okabe_ito, line: { color: okabe_ito, width: 1 } }
                }
            ];
        }
    });
});
</script>

<template>
    <section>
        <h2 class="title">{{ title }}</h2>
        <p class="subtitle">{{ description }}</p>
        <div class="flex flex-row gap-5">
            <table class="basis-1/3 border-collapse text-right">
                <tbody>
                    <tr v-for="line in listeStructures" :key="line.structure.uid">
                        <th>{{ structureName(line.structure) }}</th>
                        <td>{{ formatCurrency(parseFloat(line.montant)) }}</td>
                    </tr>
                </tbody>
            </table>
            <Graph :data :layout style="min-height: 20rem" />
        </div>
        <div class="flex flex-wrap">
            <RouterLink to="/acheteurs">
                <Button :label="btn_label" variant="text" severity="secondary" icon="pi pi-list" />
            </RouterLink>
        </div>
    </section>
</template>
