<script setup lang="ts">
import { getCategorieDepartement } from '@/client';
import { getNomDepartement } from '@/service/Departements';
import { okabe_ito } from '@/service/GraphColorsService';
import { onMounted, ref } from 'vue';

import type { SankeyData } from 'plotly.js-dist';

const data = ref<Partial<SankeyData>[]>([
    {
        type: 'sankey',
        orientation: 'h',
        node: {
            label: [],
            color: okabe_ito
        },
        link: {
            source: [],
            target: [],
            value: []
        }
    }
]);
const layout = { margin: { l: 0, t: 0, b: 20, r: 0 } };

onMounted(() => {
    const departementsRegion = settings.departements.split(',');

    getCategorieDepartement().then((response) => {
        if (response.data) {
            function getOrCreateLabel(label: string): number {
                let indice = data.value[0].node?.label?.indexOf(label) as number;
                if (indice == -1) {
                    indice = data.value[0].node?.label?.length as number;
                    data.value[0].node?.label?.push(label);
                }
                return indice;
            }
            let montantAutresRegionsBySource = { Travaux: 0, Fournitures: 0, Services: 0 };
            for (let line of response.data) {
                if (departementsRegion.includes(line.code)) {
                    data.value[0].link?.value?.push(parseFloat(line.montant));
                    data.value[0].link?.source?.push(getOrCreateLabel(line.categorie));
                    data.value[0].link?.target?.push(getOrCreateLabel('(' + line.code + ') ' + getNomDepartement(line.code)));
                } else {
                    montantAutresRegionsBySource[line.categorie] += parseFloat(line.montant);
                }
            }
            for (const [k, v] of Object.entries(montantAutresRegionsBySource)) {
                data.value[0].link?.value?.push(v);
                data.value[0].link?.source?.push(getOrCreateLabel(k));
                data.value[0].link?.target?.push(getOrCreateLabel('Départements hors région'));
            }
        }
    });
});
</script>
<template>
    <section>
        <h2 class="title">Distribution des achats par département</h2>
        <Graph :data :layout />
        <details>
            <summary>💡 Comment lire ce graphique ?</summary>
            <div>
                <h3>Comment lire ce graphique ?</h3>
                <p>
                    Le <strong>côté gauche</strong> montre les grandes catégories de marchés publics. Ces catégories sont triées par le montant total des marchés qu’elles représentent. Au survol de ces catégories, on met en surbrillance tous les
                    liens avec les départements qui ont lancé le marché.
                </p>
                <p>Le <strong>côté droit</strong> montre les départements triés par la première catégorie de gauche. Au survol de ces départements, on met en surbrillance tous les liens avec les catégories auxquelles correspondent leurs marchés.</p>
                <p>Au survol des <strong>liens</strong>, on obtient des informations complémentaires sur la catégorie du marché et le département lié.</p>
            </div>
        </details>
    </section>
</template>
