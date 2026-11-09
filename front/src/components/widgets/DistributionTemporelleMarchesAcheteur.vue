<script setup lang="ts">
import { getNow } from '@/service/HelpersService';
import { useMarchesPerimetre } from '@/service/UseMarchesPerimetre';

import type { PropType } from 'vue';

const props = defineProps({
    acheteurSiret: { type: String as PropType<string | null>, required: false },
    dateMin: { type: Date, default: new Date(settings.date_min) },
    dateMax: { type: Date, default: getNow() }
});

const marches = useMarchesPerimetre(() => ({ acheteurSiret: props.acheteurSiret, dateMin: props.dateMin, dateMax: props.dateMax }));
</script>

<template>
    <DistributionTemporelleMarches :marches :acheteurSiret :dateMin :dateMax />
</template>
