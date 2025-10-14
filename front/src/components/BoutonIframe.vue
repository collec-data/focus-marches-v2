<script setup lang="ts">
import { ref } from 'vue';
import { useRoute } from 'vue-router';

const props = defineProps({
    path: String,
    name: { type: String },
    acheteurUid: { type: [String, null] }
});

const route = useRoute();
const show = !route.path.includes('widget');

let query = '?';
if (props.acheteurUid) {
    query = query + 'acheteurUid=' + props.acheteurUid + '&';
}
for (const [k, v] of Object.entries(route.query)) {
    query = query + k + '=' + v + '&';
}

const label = ref('Intégrer le widget');
async function genUrl() {
    let url = '<iframe src="' + window.origin + '/widget/' + props.path + query + '" referrerpolicy="strict-origin-when-cross-origin" style="border: 0; overflow: hidden;" title="' + props.name + '" width="100%" height="600px"></iframe>';
    await navigator.clipboard.writeText(url);
    label.value = 'Copié dans le presse-papier !';
}
</script>

<template>
    <div v-if="show" class="text-right w-full p-3">
        <Button :label icon="pi pi-fw pi-code" iconPos="left" size="small" severity="info" variant="outlined" class="!w-fit" @click="genUrl" />
    </div>
</template>
