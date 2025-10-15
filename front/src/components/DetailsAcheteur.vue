<script setup lang="ts">
import type { StructureEtendueDto } from '@/client';
import { ref, watchEffect } from 'vue';

import type { PropType } from 'vue';

const props = defineProps({
    acheteur: { type: Object as PropType<Partial<StructureEtendueDto>>, default: () => ({}) }
});

const acheteur = ref<Partial<StructureEtendueDto>>(props.acheteur);
watchEffect(() => {
    acheteur.value = props.acheteur;
});
</script>

<template>
    <section class="mb-10">
        <h2>Localisation et contexte</h2>
        <div class="grid grid-cols-12 gap-5">
            <LeafletMap :lon="acheteur.lon" :lat="acheteur.lat" :label="acheteur.nom + '<br>' + acheteur.adresse" class="col-span-12 xl:col-span-6" />
            <table class="col-span-12 xl:col-span-6">
                <tbody>
                    <tr>
                        <th>Dénomination</th>
                        <td>{{ acheteur.nom }}</td>
                    </tr>
                    <tr>
                        <th>Date création</th>
                        <td></td>
                    </tr>
                    <tr>
                        <th>Sigle</th>
                        <td>{{ acheteur.sigle }}</td>
                    </tr>
                    <tr>
                        <th>Adresse</th>
                        <td>{{ acheteur.adresse }}</td>
                    </tr>
                    <tr>
                        <th>Cat entreprise</th>
                    </tr>
                    <tr>
                        <th>Cat juridique</th>
                        <td>{{ acheteur.cat_juridique }}</td>
                    </tr>
                    <tr>
                        <th>NAF</th>
                        <td>{{ acheteur.naf }}</td>
                    </tr>
                    <tr>
                        <th>Effectifs</th>
                        <td>{{ acheteur.effectifs }} (en {{ acheteur.date_effectifs }})</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </section>
</template>

<style scoped>
table th {
    font-size: 0.8rem;
    text-transform: uppercase;
    text-align: left;
    font-weight: normal;
}

table td,
table th {
    padding: 0.5rem;
}
table tr:nth-child(2n) {
    border-top: 1px solid var(--p-neutral-300);
    border-bottom: 1px solid var(--p-neutral-300);
    background-color: var(--p-neutral-100);
}
</style>
