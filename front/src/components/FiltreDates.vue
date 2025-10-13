<script setup lang="ts">
import { ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const router = useRouter();
const route = useRoute();

const props = defineProps({
    dateMin: { type: [Date, null], default: null },
    dateMax: { type: [Date, null], default: null }
});

const dates = ref({
    min: props.dateMin,
    max: props.dateMax
});

function updateDateLimits(event: SubmitEvent) {
    router.push({
        name: route.name,
        params: route.params,
        query: {
            ...route.query,
            dateMin: dates.value.min ? dates.value.min.toISOString().substring(0, 10) : null,
            dateMax: dates.value.max ? dates.value.max.toISOString().substring(0, 10) : null
        }
    });
    event.preventDefault();
}
</script>

<template>
    <Panel header="Filtrer les contrats (optionnel)">
        <form class="flex flex-row place-content-center gap-5" @submit="updateDateLimits">
            <FloatLabel variant="on">
                <label for="min">Date de début</label>
                <DatePicker v-model="dates.min" inputId="min" name="min" updateModelType="date" showIcon showButtonBar />
            </FloatLabel>
            <FloatLabel variant="on">
                <label for="max">Date de fin </label>
                <DatePicker v-model="dates.max" inputId="max" name="max" updateModelType="date" showIcon showButtonBar />
            </FloatLabel>
            <Button type="submit" label="Filtrer" severity="secondary" />
        </form>
    </Panel>
</template>
