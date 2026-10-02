<script setup lang="ts">
import { getCategorieDepartement } from '@/client';
import { getNomDepartement } from '@/service/Departements';
import { okabe_ito } from '@/service/GraphColorsService';
import { useReactiveFetch } from '@/utils/query';
import { computed } from 'vue';

import type { SankeyData } from 'plotly.js-dist';

const layout = { margin: { l: 0, t: 0, b: 20, r: 0 } };

const { etat, refetch } = useReactiveFetch(
    getCategorieDepartement,
    computed(() => ({}))
);

const data = computed<Partial<SankeyData>[] | null>(() => {
    if (etat.value.statut !== 'succes') {
        // On ne construit pas de diagramme construit tant que la réponse n'est pas reçue.
        return null;
    }
    const departementsRegion = settings.departements.split(',');
    const trace: Partial<SankeyData> = {
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
    };

    function getOrCreateLabel(label: string): number {
        let indice = trace.node?.label?.indexOf(label) as number;
        if (indice == -1) {
            indice = trace.node?.label?.length as number;
            trace.node?.label?.push(label);
        }
        return indice;
    }

    const montantAutresRegionsBySource = { Travaux: 0, Fournitures: 0, Services: 0 };
    for (const line of etat.value.data) {
        if (departementsRegion.includes(line.code)) {
            trace.link?.value?.push(parseFloat(line.montant));
            trace.link?.source?.push(getOrCreateLabel(line.categorie));
            trace.link?.target?.push(getOrCreateLabel('(' + line.code + ') ' + getNomDepartement(line.code)));
        } else {
            montantAutresRegionsBySource[line.categorie] += parseFloat(line.montant);
        }
    }
    for (const [categorie, montant] of Object.entries(montantAutresRegionsBySource)) {
        trace.link?.value?.push(montant);
        trace.link?.source?.push(getOrCreateLabel(categorie));
        trace.link?.target?.push(getOrCreateLabel('Départements hors région'));
    }

    return [trace];
});
</script>
<template>
    <section>
        <h2 class="title">Distribution des achats par département</h2>
        <ErreurChargement v-if="etat.statut === 'erreur'" :erreur="etat.erreur" message="Le chargement de la distribution par département a échoué" class="my-4" @retry="refetch" />
        <ChargementEnCours v-else-if="!data" libelle="Chargement de la distribution par département" />
        <Graph v-else :data :layout title="Distribution croisée des achats par département et par catégorie d'achat" />
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
