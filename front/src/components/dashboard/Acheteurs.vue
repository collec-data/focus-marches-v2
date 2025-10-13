<script setup lang="ts">
import { listAcheteursStructureAcheteurGet } from '@/client';
import { formatCurrency } from '@/service/HelpersService';
import { onMounted, ref } from 'vue';

import type { StructureAggMarchesDto } from '@/client';
import type { Layout, PlotData } from 'plotly.js-dist';

const listeAcheteurs = ref<Array<StructureAggMarchesDto>>([]);

const data = ref<Partial<PlotData>[]>();
const layout = { margin: { t: 0 } } as Partial<Layout>;

function transform(input: Array<StructureAggMarchesDto>) {
    let output = {
        structures: [] as Array<string | null>,
        montants: [] as Array<string>
    };
    for (var line of input) {
        output.structures.push(line.structure.nom);
        output.montants.push(line.montant);
    }
    return output;
}

onMounted(() => {
    listAcheteursStructureAcheteurGet({
        query: { limit: 12 }
    }).then((response) => {
        if (response.data) {
            listeAcheteurs.value = response.data;
            let rawData = transform(response.data);
            data.value = [
                {
                    x: rawData.structures,
                    y: rawData.montants,
                    type: 'bar'
                }
            ];
        }
    });
});
</script>

<template>
    <section>
        <h2 class="title">Qui achète ?</h2>
        <p class="subtitle">Top 12 des acheteurs classés par montant total des contrats conclus au cours de 56 derniers mois. Survolez les noms les acheteurs pour les afficher en entier.</p>
        <div class="flex flex-row gap-5">
            <table class="basis-1/3 border-collapse text-right">
                <tbody>
                    <tr v-for="line in listeAcheteurs" :key="line.structure.uid">
                        <th>{{ line.structure.nom }}</th>
                        <td>{{ formatCurrency(parseFloat(line.montant)) }}</td>
                    </tr>
                </tbody>
            </table>
            <Graph :data :layout />
        </div>
        <div class="flex flex-wrap">
            <RouterLink to="/acheteurs">
                <Button label="Liste complète des organismes acheteurs" variant="text" severity="secondary" icon="pi pi-list" />
            </RouterLink>
        </div>
    </section>
</template>
