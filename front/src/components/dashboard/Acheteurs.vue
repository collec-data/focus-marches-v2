<script setup>
import { listAcheteursStructureAcheteurGet } from '@/client';
import { onMounted, ref } from 'vue';

const listeAcheteurs = ref({});

const graphData = ref({
    labels: [],
    datasets: [{ data: [], backgroundColor: ['rgba(255, 99, 132, 0.2)', 'rgba(255, 159, 64, 0.2)', 'rgba(255, 205, 86, 0.2)', 'rgba(75, 192, 192, 0.2)', 'rgba(54, 162, 235, 0.2)', 'rgba(153, 102, 255, 0.2)', 'rgba(201, 203, 207, 0.2)'] }]
});

const graphOptions = ref({
    type: 'bar',
    data: graphData,
    options: {
        indexAxis: 'y'
    }
});

function transform(input) {
    let output = { structures: [], montants: [] };
    for (var line of input) {
        output.structures.push(line.structure.type_identifiant + ' ' + line.structure.identifiant);
        output.montants.push(line.montant);
    }
    return output;
}

onMounted(() => {
    listAcheteursStructureAcheteurGet().then((response) => {
        listeAcheteurs.value = response.data;
        let rawData = transform(response.data);
        graphData.value.labels = rawData.structures;
        graphData.value.datasets[0].data = rawData.montants;
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
                    <tr v-for="line in listeAcheteurs">
                        <th>{{ line.structure.type_identifiant }} {{ line.structure.identifiant }}</th>
                        <td>{{ Math.round(line.montant) }}</td>
                    </tr>
                </tbody>
            </table>
            <Chart type="bar" :data="graphData" :options="graphOptions" class="basis-2/3" />
        </div>
        <div class="flex flex-wrap">
            <RouterLink to="/acheteurs">
                <Button label="Liste complète des organismes acheteurs" variant="text" severity="secondary" icon="pi pi-list" />
            </RouterLink>
        </div>
    </section>
</template>
