<script setup lang="ts">
import Plotly, { type SankeyData } from 'plotly.js-dist';
import locale from 'plotly.js-locales/fr';
import type { PropType } from 'vue';
import { onBeforeUnmount, onMounted, ref, useId, watchEffect } from 'vue';

Plotly.register(locale);
Plotly.setPlotConfig({ locale: 'fr' });

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
    },
    title: {
        type: String,
        required: true
    }
});

const chartId = useId();
let chartRendered = false;
const label = ref(buildLabel());

function buildLabel(): string {
    let label = 'Ce graphique est intitulé « ' + props.title + ' ». ';

    if (props.data && props.data[0]) {
        switch (props.data[0].type) {
            case 'pie':
                if (props.data[0].values && props.data[0].labels) {
                    label = label + 'Les données sont : ';
                    for (let i = 0; i < props.data[0].values.length; i++) {
                        label = label + (props.data[0].labels[i] ? props.data[0].labels[i]?.toString().replaceAll('<br>', ' ') : 'aucun(e)') + ' ' + props.data[0].values[i] + ', ';
                    }
                    label = label.slice(0, -2) + '.'; // remove last comma
                }
                break;

            case 'bar':
                if (props.data[0].x && props.data[0].y) {
                    label = label + 'Les données sont : ';
                    for (let i = 0; i < props.data[0].x.length; i++) {
                        label = label + (props.data[0].y[i] ? props.data[0].y[i]?.toString().replaceAll('<br>', ' ') : 'aucun(e)') + ' ' + props.data[0].x[i] + ', ';
                    }
                    label = label.slice(0, -2) + '.'; // remove last comma
                }
                break;
            case 'sankey': {
                const sankey_data = props.data[0] as Partial<SankeyData>;
                label = label + 'Les données sont : ';
                for (let i = 0; i < (sankey_data.link?.source?.length ?? 0); i++) {
                    label = label + sankey_data.link!.value![i] + '€ de ' + sankey_data.node!.label![sankey_data.link!.source![i]] + '  dans ' + sankey_data.node!.label![sankey_data.link!.target![i]] + ', ';
                }
                label = label.slice(0, -2) + '.'; // remove last comma
                break;
            }
            case 'scatter':
                label = label + 'Il contient un trop gros volume de données pour être compréhensible textuellement.';
                break;
            default:
                console.log('Graphique non accessible ' + props.title + '(type : ' + props.data[0].type + ')');
                break;
        }
    }
    return label;
}

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
            Plotly.newPlot(chartId, props.data, props.layout, { ...props.config, ...{ responsive: true } }).then(() => {
                chartRendered = true;
            });
            label.value = buildLabel();
        }
    });
});

onBeforeUnmount(removeChart);
</script>

<template>
    <div :id="chartId" role="figure" class="chart" :aria-label="label" />
</template>
