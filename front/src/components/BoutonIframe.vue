<script setup lang="ts">
import { useLayout } from '@/layout/composables/layout';
import { ref } from 'vue';
import { useRoute } from 'vue-router';

const { layoutConfig } = useLayout();

const props = defineProps({
    path: String,
    name: { type: String },
    acheteurSiret: { type: [String, null] }
});

const route = useRoute();
const show = !route.path.includes('widget');

const label = ref('Intégrer le widget');
async function genUrl() {
    const layoutParams = { color_primary: layoutConfig.primary, preset: layoutConfig.preset };
    if (layoutConfig.surface) {
        layoutParams['color_surface'] = layoutConfig.surface;
    }

    const query = new URLSearchParams({
        ...(props.acheteurSiret ? { siret: props.acheteurSiret } : null),
        ...route.query,
        ...layoutParams
    }).toString();
    let url = '<iframe src="' + window.origin + '/widget/' + props.path + '?' + query + '" referrerpolicy="strict-origin-when-cross-origin" style="border: 0; overflow: hidden;" title="' + props.name + '"></iframe>';
    await navigator.clipboard.writeText(url);
    label.value = 'Copié dans le presse-papier !';
}
</script>

<template>
    <div v-if="show" class="text-right w-full p-3">
        <Button :label icon="pi pi-fw pi-code" iconPos="left" size="small" severity="info" variant="outlined" class="!w-fit" @click="genUrl" />
    </div>
</template>
