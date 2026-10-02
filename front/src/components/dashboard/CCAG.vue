<script setup lang="ts">
import { getMarchesParCcag } from '@/client';
import { okabe_ito } from '@/service/GraphColorsService';
import { breakLongLabel } from '@/service/HelpersService';
import { useStructureIdentifiee } from '@/service/UseStructureIdentifiee';
import { useReactiveFetch } from '@/utils/query';
import { computed } from 'vue';

import type { MarcheCcagDto } from '@/client';
import type { PropType } from 'vue';
import type { Layout, PlotData } from 'plotly.js-dist';

// Pas de valeur par défaut : `undefined` signifie « acheteur encore non identifié », `null` « aucun acheteur demandé ».
const props = defineProps({
    acheteurUid: { type: Number as PropType<number | null>, required: false },
    acheteurSiret: { type: String as PropType<string | null>, required: false },
    dateMin: { type: Date as PropType<Date | null>, required: false },
    dateMax: { type: Date as PropType<Date | null>, required: false }
});

interface icategorie {
    montants: Partial<PlotData>[];
    nombres: Partial<PlotData>[];
}
interface idatas {
    travaux: icategorie;
    services: icategorie;
    fournitures: icategorie;
}

const layout = { margin: { l: 150, t: 0, b: 20, r: 0 } } as Layout;

function transform(input: Array<MarcheCcagDto>): idatas {
    const common = {
        type: 'bar',
        orientation: 'h',
        marker: { color: okabe_ito, line: { color: okabe_ito, width: 1 } }
    };
    let output = <idatas>{
        travaux: { montants: [{ x: [], y: [], ...common }], nombres: [{ x: [], y: [], ...common }] },
        services: { montants: [{ x: [], y: [], ...common }], nombres: [{ x: [], y: [], ...common }] },
        fournitures: { montants: [{ x: [], y: [], ...common }], nombres: [{ x: [], y: [], ...common }] }
    };
    for (var line of input) {
        const key = line.categorie.toLowerCase();
        if (line.ccag) {
            output[key].montants[0].y.push(breakLongLabel(line.ccag));
            output[key].nombres[0].y.push(breakLongLabel(line.ccag));
        } else {
            output[key].montants[0].y.push('Sans CCAG');
            output[key].nombres[0].y.push('Sans CCAG');
        }
        output[key].montants[0].x.push(parseFloat(line.montant));
        output[key].nombres[0].x.push(line.nombre);
    }
    return output;
}

const {
    uid,
    erreur: erreurAcheteur,
    refetch: refetchAcheteur
} = useStructureIdentifiee(
    () => props.acheteurUid,
    () => props.acheteurSiret
);

const options = computed(() => {
    if (uid.value === undefined) {
        return undefined;
    }
    return {
        query: {
            date_debut: props.dateMin ?? undefined,
            date_fin: props.dateMax ?? undefined,
            acheteur_uid: uid.value ?? undefined
        }
    };
});

const { etat, refetch } = useReactiveFetch(getMarchesParCcag, options);

// On ne dessine rien avant la réponse : un graphique à zéro barre laisserait croire à une absence de contrats.
const datas = computed<Partial<idatas>>(() => (etat.value.statut === 'succes' ? transform(etat.value.data) : {}));
</script>

<template>
    <section>
        <h2 class="title">Cahier des clauses administratives et générales utilisés</h2>

        <ErreurChargement v-if="erreurAcheteur" :erreur="erreurAcheteur" message="Aucune structure ne correspond à ce SIRET" @retry="refetchAcheteur" />
        <ErreurChargement v-else-if="etat.statut === 'erreur'" :erreur="etat.erreur" message="Le chargement des CCAG a échoué" @retry="refetch" />
        <ChargementEnCours v-else-if="etat.statut !== 'succes'" libelle="Chargement des CCAG" />

        <Tabs v-else value="services">
            <TabList>
                <Tab value="services">Services</Tab>
                <Tab value="travaux">Travaux</Tab>
                <Tab value="fournitures">Fournitures</Tab>
            </TabList>
            <TabPanels>
                <TabPanel value="services">
                    <div class="grid grid-cols-12 gap-8">
                        <div class="col-span-12 xl:col-span-6">
                            <h3>Montant des contrats par CCAG</h3>
                            <Graph :data="datas.services?.montants" :layout title="Montant des contrats de service" />
                        </div>
                        <div class="col-span-12 xl:col-span-6">
                            <h3>Nombre de contrats par CCAG</h3>
                            <Graph :data="datas.services?.nombres" :layout title="Nombre de contrats de service" />
                        </div>
                    </div>
                </TabPanel>
                <TabPanel value="travaux">
                    <div class="grid grid-cols-12 gap-8">
                        <div class="col-span-12 xl:col-span-6">
                            <h3>Montant des contrats par CCAG</h3>
                            <Graph :data="datas.travaux?.montants" :layout title="Montant des contrats de travaux " />
                        </div>
                        <div class="col-span-12 xl:col-span-6">
                            <h3>Nombre de contrats par CCAG</h3>
                            <Graph :data="datas.travaux?.nombres" :layout title="Nombre de contrats de travaux " />
                        </div>
                    </div>
                </TabPanel>
                <TabPanel value="fournitures">
                    <div class="grid grid-cols-12 gap-8">
                        <div class="col-span-12 xl:col-span-6">
                            <h3>Montant des contrats par CCAG</h3>
                            <Graph :data="datas.fournitures?.montants" :layout title="Montant des contrats de fournitures" />
                        </div>
                        <div class="col-span-12 xl:col-span-6">
                            <h3>Nombre de contrats par CCAG</h3>
                            <Graph :data="datas.fournitures?.nombres" :layout title="Nombre de contrats de fournitures" />
                        </div>
                    </div>
                </TabPanel>
            </TabPanels>
        </Tabs>
        <BoutonIframe v-if="acheteurSiret" :path="'acheteur/' + acheteurSiret + '/marches/ccag'" name="La répartition des marchés publics par clause administrative utilisée, sous forme de graphique" />
    </section>
</template>
