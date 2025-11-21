<script setup lang="ts">
import { changePreset, getPresetExt } from '@/service/ConfiguratorService';
import { updatePreset } from '@primeuix/themes';
import { useRoute } from 'vue-router';
import { useLayout } from './composables/layout';

const route = useRoute();
const { layoutConfig } = useLayout();

if (route.query.color_primary) {
    layoutConfig.primary = route.query.color_primary as string;
}
if (route.query.color_surface) {
    layoutConfig.surface = route.query.color_surface as string;
}
updatePreset(getPresetExt(layoutConfig));

if (route.query.preset) {
    changePreset(layoutConfig, route.query.preset as string);
}
</script>

<template>
    <main class="card">
        <router-view></router-view>
    </main>
</template>
