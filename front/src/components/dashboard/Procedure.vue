<script setup lang="ts">
import { getMarchesParProcedureMarcheProcedureGet } from '@/client';
import { onMounted, ref } from 'vue';

import type { MarcheProcedureDto } from '@/client';

const props = defineProps({
    acheteurUid: { type: [String, null], default: null },
    vendeurUid: { type: [String, null], default: null }
});

const graphNombreData = ref({
    labels: [] as Array<number | null>,
    datasets: [
        {
            label: 'Contrats pour la procédure',
            data: [] as Array<number | null>,
            backgroundColor: ['rgba(255, 99, 132, 0.2)', 'rgba(255, 159, 64, 0.2)', 'rgba(255, 205, 86, 0.2)', 'rgba(75, 192, 192, 0.2)', 'rgba(54, 162, 235, 0.2)', 'rgba(153, 102, 255, 0.2)']
        }
    ]
});
const graphNombreOptions = ref({
    type: 'bar',
    data: graphNombreData,
    options: {
        indexAxis: 'y',
        responsive: true
    },
    plugins: {
        title: {
            align: 'start',
            display: true,
            text: 'Nombre de contrats par procédure'
        }
    }
});

const graphMontantsData = ref({
    labels: [] as Array<number | null>,
    datasets: [
        {
            label: 'Montants pour la procédure',
            data: [] as Array<string | null>,
            backgroundColor: ['rgba(255, 99, 132, 0.2)', 'rgba(255, 159, 64, 0.2)', 'rgba(255, 205, 86, 0.2)', 'rgba(75, 192, 192, 0.2)', 'rgba(54, 162, 235, 0.2)', 'rgba(153, 102, 255, 0.2)']
        }
    ]
});
const graphMontantsOptions = ref({
    type: 'bar',
    data: graphMontantsData,
    options: {
        indexAxis: 'y',
        responsive: true
    },
    plugins: {
        title: {
            align: 'start',
            display: true,
            text: 'Montant des contrats par procédure'
        }
    }
});

function transform(input: Array<MarcheProcedureDto>) {
    let output = {
        procedure: [] as Array<number | null>,
        montant: [] as Array<string>,
        nombre: [] as Array<number>
    };
    for (var line of input) {
        output.procedure.push(line.procedure);
        output.montant.push(line.montant);
        output.nombre.push(line.nombre);
    }
    return output;
}

onMounted(() => {
    getMarchesParProcedureMarcheProcedureGet({
        query: {
            date_debut: new Date('2010-01-01'),
            acheteur_uid: props.acheteurUid,
            vendeur_uid: props.vendeurUid
        }
    }).then((data) => {
        if (data.data) {
            let raw_data = transform(data.data);
            graphNombreData.value.labels = raw_data.procedure;
            graphNombreData.value.datasets[0].data = raw_data.nombre;
            graphMontantsData.value.labels = raw_data.procedure;
            graphMontantsData.value.datasets[0].data = raw_data.montant;
        }
    });
});
</script>

<template>
    <Fluid class="grid grid-cols-12 gap-8">
        <div class="col-span-12">
            <h2 class="title">Procédure suivie</h2>
            <p class="subtitle">Classement des contrats selon la procédure suivie lors de la consultation. La période observée est de XX mois</p>
        </div>
        <div class="col-span-12 xl:col-span-6">
            <Chart type="bar" :data="graphMontantsData" :options="graphMontantsOptions" />
        </div>
        <div class="col-span-12 xl:col-span-6">
            <Chart type="bar" :data="graphNombreData" :options="graphNombreOptions" />
        </div>
    </Fluid>
</template>
