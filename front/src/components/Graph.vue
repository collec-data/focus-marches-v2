<script setup lang="ts">
import Plotly from 'plotly.js-dist';
import type { PropType } from 'vue';
import { onBeforeUnmount, onMounted, useId, watchEffect } from 'vue';

const props = defineProps({
    data: { type: Array as PropType<Plotly.Data[]> },
    layout: {
        required: false,
        type: Object as PropType<Partial<Plotly.Layout>>,
        default: undefined
    },
    config: {
        required: false,
        type: Object as PropType<Partial<Plotly.Config>>,
        default: undefined
    }
});

const chartId = useId();
let chartRendered = false;

function removeChart() {
    if (chartRendered) {
        Plotly.purge(chartId);
        chartRendered = false;
    }
}

onMounted(() => {
    watchEffect(() => {
        removeChart();
        if (props.data) {
            Plotly.newPlot(chartId, props.data, props.layout, props.config).then(() => {
                chartRendered = true;
            });
        }
    });
});

onBeforeUnmount(removeChart);
</script>

<template>
    <div :id="chartId" class="chart" />
</template>
