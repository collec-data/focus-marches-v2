<script setup lang="ts">
import { getStructureId, type StructureEtendueDto } from '@/client';
import { formatDate, getCatEntreprise, structureName } from '@/service/HelpersService';
import { onMounted, ref, watchEffect } from 'vue';

import type { PropType } from 'vue';

const props = defineProps({
    acheteur: { type: Object as PropType<Partial<StructureEtendueDto>>, default: () => ({}) },
    acheteurSiret: { type: [String, null], default: null }
});

const acheteur = ref<Partial<StructureEtendueDto>>(props.acheteur);
watchEffect(() => {
    acheteur.value = props.acheteur;
});

onMounted(() => {
    if (props.acheteurSiret) {
        getStructureId({ path: { id: props.acheteurSiret, type_id: 'SIRET' } }).then((response) => {
            if (response.data) {
                acheteur.value = response.data;
            }
        });
    }
});
</script>

<template>
    <section class="mb-10">
        <h2>Localisation et contexte</h2>
        <div class="grid grid-cols-12 gap-5">
            <LeafletMap :lon="acheteur.longitude" :lat="acheteur.latitude" :label="structureName(acheteur) + '<br>' + acheteur.adresse" class="col-span-12 xl:col-span-6" />
            <table class="col-span-12 xl:col-span-6">
                <tbody>
                    <tr>
                        <th>Dénomination</th>
                        <td>{{ acheteur.nom }}</td>
                    </tr>
                    <tr>
                        <th>Date création</th>
                        <td>{{ acheteur.date_creation ? formatDate(acheteur.date_creation) : '' }}</td>
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
                        <td>{{ getCatEntreprise(acheteur.cat_entreprise) }}</td>
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
        <BoutonIframe :path="'acheteur/' + acheteur.identifiant + '/details'" :name="'Localisation et données administratives de ' + acheteur.nom" />
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
