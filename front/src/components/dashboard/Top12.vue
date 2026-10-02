<script setup lang="ts">
import { CategorieMarche, listAcheteurs, listVendeurs } from '@/client';
import { okabe_ito } from '@/service/GraphColorsService';
import { breakLongLabel, formatCurrency, formatNumber, getDurationInMonths, getNow, structureName } from '@/service/HelpersService';
import { useStructureIdentifiee } from '@/service/UseStructureIdentifiee';
import { useReactiveFetch } from '@/utils/query';
import type { ErreurReactiveFetch } from '@/utils/query';
import { computed, ref } from 'vue';

import type { StructureAggMarchesDto } from '@/client';
import type { PropType } from 'vue';
import type { Layout, PlotData } from 'plotly.js-dist';

// Pas de valeur par défaut : `undefined` signifie « acheteur encore non identifié », `null` « aucun acheteur demandé ».
const props = defineProps({
    type: String,
    acheteurUid: { type: Number as PropType<number | null>, required: false },
    acheteurSiret: { type: String as PropType<string | null>, required: false },
    vendeurUid: { type: Number as PropType<number | null>, required: false },
    dateMin: { type: Date, default: new Date(settings.date_min) },
    dateMax: { type: Date, default: getNow() }
});

type Categorie = keyof typeof CATEGORIES;

type Graphiques = Record<string, Partial<PlotData>[]>;
const graphesVides = (): Graphiques => ({ tout: [], services: [], travaux: [], fournitures: [] });

const CATEGORIES = { tout: undefined, services: CategorieMarche.SERVICES, travaux: CategorieMarche.TRAVAUX, fournitures: CategorieMarche.FOURNITURES } as const;

let title = '';
let description = '';
let btn_label = '';
let link_path = '';

if (props.type == 'acheteurs') {
    title = 'Qui achète ?';
    description = 'Top 12 des acheteurs classés par montant total des contrats conclus au cours des ' + getDurationInMonths(props.dateMin, props.dateMax) + ' derniers mois. Survolez les noms les acheteurs pour les afficher en entier.';
    btn_label = 'Liste complète des organismes acheteurs';
    link_path = '/acheteur/';
} else {
    title = 'Qui réalise ?';
    description = 'Top 12 des fournisseurs classés par montant total des contrats remportés au cours des ' + getDurationInMonths(props.dateMin, props.dateMax) + ' derniers mois. Survolez les noms des fournisseurs pour les afficher en entier.';
    btn_label = 'Liste complète des fournisseurs';
    link_path = '/fournisseur/';
}

const layout = {
    margin: { t: 0, b: 200, r: 100 },
    xaxis: {
        tickangle: 45
    }
} as Partial<Layout>;

function transform(input: Array<StructureAggMarchesDto>) {
    let output = {
        structures: [] as Array<string | null>,
        montants: [] as Array<string>
    };
    for (var line of input) {
        output.structures.push(breakLongLabel(structureName(line.structure), 30));
        output.montants.push(line.montant);
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

function options(categorie: CategorieMarche | undefined, limite: number | null, actif: () => boolean) {
    return computed(() => {
        if (uid.value === undefined || !actif()) {
            return undefined;
        }
        return {
            query: {
                limit: limite,
                acheteur_uid: uid.value ?? undefined,
                vendeur_uid: props.vendeurUid ?? undefined,
                date_debut: props.dateMin ?? undefined,
                date_fin: props.dateMax ?? undefined,
                categorie: categorie
            }
        };
    });
}

// Chaque onglet a sa propre requête, déclenchée à sa première visite puis rejouée à chaque changement de période.
// Les onglets non encore visités ne consomment aucune requête.
const ongletsVisites = ref<Set<Categorie>>(new Set(['tout']));
const lister = () => (props.type === 'acheteurs' ? listAcheteurs : listVendeurs);

const parCategorie = Object.fromEntries(
    (Object.keys(CATEGORIES) as Categorie[]).map((cle) => [
        cle,
        useReactiveFetch(
            lister(),
            options(CATEGORIES[cle], 12, () => ongletsVisites.value.has(cle))
        )
    ])
) as Record<Categorie, ReturnType<typeof useReactiveFetch<typeof listAcheteurs, never>>>;

const showModale = ref(false);
const exhaustive = useReactiveFetch(
    lister(),
    options(undefined, null, () => showModale.value)
);

const reussite = computed(() => Object.values(parCategorie).every((requete) => requete.etat.value.statut === 'succes'));
const premiereErreur = computed<ErreurReactiveFetch | null>(() => {
    for (const requete of Object.values(parCategorie)) {
        if (requete.etat.value.statut === 'erreur') {
            return requete.etat.value.erreur;
        }
    }
    return null;
});

const listeStructures = computed(() => {
    const sortie = {} as Record<Categorie, StructureAggMarchesDto[]>;
    for (const cle of Object.keys(CATEGORIES) as Categorie[]) {
        const requete = parCategorie[cle];
        sortie[cle] = requete.etat.value.statut === 'succes' ? requete.etat.value.data.items : [];
    }
    return sortie;
});

const listeExhaustiveStructures = computed<StructureAggMarchesDto[]>(() => (exhaustive.etat.value.statut === 'succes' ? exhaustive.etat.value.data.items : []));
const etatExhaustive = computed(() => exhaustive.etat.value);

const data = computed<Graphiques>(() => {
    const sortie = graphesVides();
    for (const cle of Object.keys(CATEGORIES) as Categorie[]) {
        const requete = parCategorie[cle];
        if (requete.etat.value.statut !== 'succes') {
            continue;
        }
        const brut = transform(requete.etat.value.data.items);
        sortie[cle] = [
            {
                x: brut.structures,
                y: brut.montants,
                type: 'bar',
                marker: { color: okabe_ito, line: { color: okabe_ito, width: 1 } }
            }
        ];
    }
    return sortie;
});

function change(categorie: string | number) {
    const cle = String(categorie).toLowerCase() as Categorie;
    if (ongletsVisites.value.has(cle)) {
        return;
    }
    ongletsVisites.value = new Set(ongletsVisites.value).add(cle);
}

function openModale() {
    showModale.value = true;
    // on recharge systématiquement à l'ouverture au cas où les filtres auraient changé
    exhaustive.refetch();
}
</script>

<template>
    <section>
        <h2 class="title">{{ title }}</h2>
        <p class="subtitle">{{ description }}</p>

        <ErreurChargement v-if="erreurAcheteur" :erreur="erreurAcheteur" message="Aucune structure ne correspond à ce SIRET" @retry="refetchAcheteur" />
        <ErreurChargement v-else-if="premiereErreur" :erreur="premiereErreur" message="Le chargement du classement a échoué" @retry="() => Object.values(parCategorie).forEach((requete) => requete.refetch())" />

        <Tabs v-else-if="reussite" value="tout" @update:value="change">
            <TabList>
                <Tab value="tout">Tous les marchés</Tab>
                <Tab :value="CategorieMarche.SERVICES">{{ CategorieMarche.SERVICES }}</Tab>
                <Tab :value="CategorieMarche.TRAVAUX">{{ CategorieMarche.TRAVAUX }}</Tab>
                <Tab :value="CategorieMarche.FOURNITURES">{{ CategorieMarche.FOURNITURES }}</Tab>
            </TabList>
            <TabPanels>
                <TabPanel value="tout">
                    <div class="flex flex-row gap-5">
                        <table class="basis-1/3 border-collapse text-right">
                            <tbody>
                                <tr v-for="line in listeStructures.tout" :key="line.structure.uid">
                                    <th>{{ structureName(line.structure) }}</th>
                                    <td>{{ formatCurrency(parseFloat(line.montant)) }}</td>
                                </tr>
                            </tbody>
                        </table>
                        <div class="basis-2/3">
                            <Graph :data="data.tout" :layout style="min-height: 25rem" title="Montant des contrats du top 12 toutes catégories confondues" />
                        </div>
                    </div>
                </TabPanel>
                <TabPanel :value="CategorieMarche.SERVICES">
                    <div class="flex flex-row gap-5">
                        <table class="basis-1/3 border-collapse text-right">
                            <tbody>
                                <tr v-for="line in listeStructures.services" :key="line.structure.uid">
                                    <th>{{ structureName(line.structure) }}</th>
                                    <td>{{ formatCurrency(parseFloat(line.montant)) }}</td>
                                </tr>
                            </tbody>
                        </table>
                        <div class="basis-2/3">
                            <Graph :data="data.services" :layout style="min-height: 25rem" title="Montant des contrats du top 12 des services" />
                        </div>
                    </div>
                </TabPanel>
                <TabPanel :value="CategorieMarche.TRAVAUX">
                    <div class="flex flex-row gap-5">
                        <table class="basis-1/3 border-collapse text-right">
                            <tbody>
                                <tr v-for="line in listeStructures.travaux" :key="line.structure.uid">
                                    <th>{{ structureName(line.structure) }}</th>
                                    <td>{{ formatCurrency(parseFloat(line.montant)) }}</td>
                                </tr>
                            </tbody>
                        </table>
                        <div class="basis-2/3">
                            <Graph :data="data.travaux" :layout style="min-height: 25rem" title="Montant des contrats du top 12 des travaux" />
                        </div>
                    </div>
                </TabPanel>
                <TabPanel :value="CategorieMarche.FOURNITURES">
                    <div class="flex flex-row gap-5">
                        <table class="basis-1/3 border-collapse text-right">
                            <tbody>
                                <tr v-for="line in listeStructures.fournitures" :key="line.structure.uid">
                                    <th>{{ structureName(line.structure) }}</th>
                                    <td>{{ formatCurrency(parseFloat(line.montant)) }}</td>
                                </tr>
                            </tbody>
                        </table>
                        <div class="basis-2/3">
                            <Graph :data="data.fournitures" :layout style="min-height: 25rem" title="Montant des contrats du top 12 des fournitures" />
                        </div>
                    </div>
                </TabPanel>
            </TabPanels>
        </Tabs>
        <div class="flex flex-wrap">
            <Button :label="btn_label" variant="text" severity="secondary" icon="pi pi-list" aria-label="Voir la liste des structures" @click="openModale" />
        </div>
        <BoutonIframe v-if="acheteurSiret" :path="'acheteur/' + acheteurSiret + '/marches/top12'" name="Le top12 des fournisseurs" />
    </section>
    <Dialog :visible="showModale" modal :header="btn_label" class="max-w-full" @update:visible="showModale = false">
        <DataTable v-if="etatExhaustive.statut !== 'succes'" :value="[]" :loading="etatExhaustive.statut === 'chargement'">
            <template #empty>
                <ErreurChargement v-if="etatExhaustive.statut === 'erreur'" :erreur="etatExhaustive.erreur" message="Le chargement de la liste a échoué" @retry="exhaustive.refetch()" />
                <ChargementEnCours v-else libelle="Chargement de la liste" />
            </template>
        </DataTable>
        <DataTable v-else :value="listeExhaustiveStructures" sortField="structure.nom" :sortOrder="1" removableSort stripedRows paginator :rows="10">
            <Column field="structure.nom" header="Nom" sortable>
                <template #body="slotProps">
                    <RouterLink :to="link_path + slotProps.data.structure.uid">
                        <Button :label="structureName(slotProps.data.structure)" as="a" variant="link" />
                    </RouterLink>
                </template>
            </Column>
            <Column field="nb_contrats" header="NB contrats" sortable>
                <template #body="{ data }">
                    {{ formatNumber(data.nb_contrats) }}
                </template>
            </Column>
            <Column field="montant" header="Montant contrats" sortable bodyStyle="text-align:right">
                <template #body="{ data }">
                    {{ formatCurrency(parseFloat(data.montant)) }}
                </template>
            </Column>
        </DataTable>
    </Dialog>
</template>
