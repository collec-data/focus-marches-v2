<script setup lang="ts">
import { useMarchesPerimetre } from '@/service/UseMarchesPerimetre';

import type { PropType } from 'vue';

const props = defineProps({
    acheteurSiret: { type: String as PropType<string | null>, required: false },
    dateMin: { type: Date as PropType<Date | null>, required: false },
    dateMax: { type: Date as PropType<Date | null>, required: false }
});

const marches = useMarchesPerimetre(() => ({ acheteurSiret: props.acheteurSiret, dateMin: props.dateMin, dateMax: props.dateMax }));
</script>

<template>
    <ListeMarches :marches :acheteurSiret />
</template>
