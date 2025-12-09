<script setup lang="ts">
import { CategorieMarche, ConsiderationsEnvironnementales, ConsiderationsSociales, FormePrix, getLieux, getListeMarches, listStructures, NatureMarche, ProcedureMarche, TechniqueAchat, TypeCodeLieu } from '@/client';
import { getNomDepartement } from '@/service/Departements';
import { formatCurrency, formatDate, getCatEntreprise, getNow, structureName } from '@/service/HelpersService';
import { onMounted, ref } from 'vue';

import type { LieuDto, MarcheAllegeDto, StructureDto } from '@/client';
import type { AutoCompleteCompleteEvent } from 'primevue';

const marches = ref<MarcheAllegeDto[]>([]);

const acheteurs = ref<StructureDto[]>([]);
const fournisseurs = ref<StructureDto[]>([]);

const options_achat_durable: string[] = (Object.values(ConsiderationsEnvironnementales) as string[]).concat(Object.values(ConsiderationsSociales) as string[]).filter((o) => !o.includes('Pas de'));

const filterOptions = {
    ignoreCase: true
};

interface departement {
    value: string;
    code: string;
}
const departements = ref<departement[]>([]);
function getDepartementsRecenses() {
    getLieux({ query: { type_lieu: TypeCodeLieu.CODE_DÉPARTEMENT } }).then((response) => {
        if (response.data) {
            departements.value = response.data.map((lieu: LieuDto) => {
                return { value: `(${lieu.code}) ${getNomDepartement(lieu.code)}`, code: lieu.code };
            });
        }
    });
}

onMounted(() => {
    getDepartementsRecenses();
});

function searchAcheteur(e: AutoCompleteCompleteEvent) {
    if (e.query.length > 1) {
        listStructures({ query: { nom: e.query.toUpperCase(), is_acheteur: true } }).then((response) => {
            if (response.data) {
                acheteurs.value = response.data;
            }
        });
    } else {
        acheteurs.value = [];
    }
}

function searchFournisseur(e: AutoCompleteCompleteEvent) {
    if (e.query.length > 1) {
        listStructures({ query: { nom: e.query.toUpperCase(), is_vendeur: true } }).then((response) => {
            if (response.data) {
                fournisseurs.value = response.data;
            }
        });
    } else {
        fournisseurs.value = [];
    }
}

const filtres = ref({
    acheteur: null as null | StructureDto,
    fournisseur: null as null | StructureDto,
    objet: null,
    cpv: null,
    code_lieu: null,
    forme_prix: null,
    type_marche: null,
    procedure: null,
    categorie: null,
    technique_achat: null,
    consideration: null,
    montant_min: null,
    montant_max: null,
    duree_min: null,
    duree_max: null,
    date_min: new Date(settings.date_min),
    date_max: getNow()
});

const query = ref({});

function fetchData() {
    query.value = {
        acheteur_uid: filtres.value.acheteur?.uid,
        vendeur_uid: filtres.value.fournisseur?.uid,
        objet: filtres.value.objet,
        cpv: filtres.value.cpv,
        code_lieu: filtres.value.code_lieu,
        type_marche: filtres.value.type_marche,
        forme_prix: filtres.value.forme_prix,
        procedure: filtres.value.procedure,
        technique_achat: filtres.value.technique_achat,
        categorie: filtres.value.categorie,
        consideration: filtres.value.consideration,
        montant_min: filtres.value.montant_min,
        montant_max: filtres.value.montant_max,
        duree_min: filtres.value.duree_min,
        duree_max: filtres.value.duree_max,
        date_debut: filtres.value.date_min.toISOString().substring(0, 10),
        date_fin: filtres.value.date_max.toISOString().substring(0, 10)
    };
    getListeMarches({
        query: {
            ...query.value
        }
    }).then((response) => {
        if (response.data) {
            marches.value = response.data;
        }
    });
}

function search(event: SubmitEvent) {
    event.preventDefault();
    fetchData();
}

const recherche_avancee = ref(false);
const marcheUid = ref(null);
</script>

<template>
    <main className="card">
        <h1>Explorez les marchés publics</h1>
        <p>Quel est l'historique d'achat d'une collectivité ? Ai-j'ai obtenu un bon prix pour mes marchés ?</p>
        <p>Découvrez les réponses à ces questions et à bien d'autres avec ces filtres de recherche.</p>

        <details>
            <summary>💡 Idées de recherches</summary>
            <div class="flex flex-row gap-10">
                <div class="basis-1/3">
                    <h3><i class="pi pi-history"></i> Quel est l'historique d'achat d'une collectivité ?</h3>
                    <p>Commencez à écrire le nom de la collectivité dans la boîte «&nbsp;acheteur&nbsp;». Au fur et mesure, des propositions vont apparaître.</p>
                    <p>Dès que vous allez répérer la collectivité qui vous intéresse, cliquez sur celle-ci, puis sur le bouton «&nbsp;Chercher&nbsp;». L'historique de ses achat s'affichera sur le tableau en bas de page.</p>
                </div>

                <div class="basis-1/3">
                    <h3><i class="pi pi-thumbs-up"></i> Comment savoir si j'ai obtenu un bon prix ?</h3>
                    <p>Les conditions des achats ne sont jamais identiques, mais vous pouvez lister tous les marchés ayant un code CPV proche du votre.</p>
                    <p>
                        La recherche sur le code CPV fonctionne de gauche à droite : si vous tapez «&nbsp;45&nbsp;» vous aurez tous les marchés de la catégorie «&nbsp;Travaux&nbsp;», tandis que si vous tapez «&nbsp;45261410&nbsp;» vous limiterez la
                        recherche aux «&nbsp;Travaux d'isolation de toiture&nbsp;».
                    </p>
                </div>
                <div class="basis-1/3">
                    <h3><i class="pi pi-search"></i> marchés ont été passés par l'ancienne équipe ?</h3>
                    <p>Renseignez d'abord la case «&nbsp;acheteur&nbsp;» avec le nom de la commune. Ensuite, cliquez sur «&nbsp;avancé&nbsp;». Vous verrez alors deux cases vous permettant de delimiter la période de recherche.</p>
                </div>
            </div>
        </details>

        <Panel header="Rechercher dans les marchés">
            <template #icons>
                <ToggleButton v-model="recherche_avancee" onLabel="Recherche simple" offLabel="Recherche avancée" />
            </template>
            <form @submit="search">
                <div class="flex flex-row gap-5 mb-5">
                    <div class="basis-1/3">
                        <label for="acheteur">Acheteur</label>
                        <AutoComplete
                            v-model="filtres.acheteur"
                            :suggestions="acheteurs"
                            optionLabel="nom"
                            inputId="acheteur"
                            name="acheteur"
                            placeholder="Organisme qui a créé la consultation"
                            showClear
                            fluid
                            :filterOptions
                            @complete="searchAcheteur"
                        />
                    </div>
                    <div class="basis-1/3">
                        <label for="fournisseur">Fournisseur</label>
                        <AutoComplete v-model="filtres.fournisseur" :suggestions="fournisseurs" optionLabel="nom" inputId="fournisseur" name="fournisseur" placeholder="Entité" showClear fluid :filterOptions @complete="searchFournisseur" />
                    </div>
                    <div class="basis-1/3">
                        <label for="objet">Objet</label>
                        <InputText v-model="filtres.objet" inputId="objet" name="objet" placeholder="Ex: ordinateur, tablette" fluid></InputText>
                    </div>
                </div>
                <div v-if="recherche_avancee" class="flex flex-row gap-5 mb-5">
                    <div class="basis-1/3">
                        <label for="code_cpv">Code CPV</label>
                        <InputText v-model="filtres.cpv" inputId="code_cpv" name="code_cpv" placeholder="Ex: 45 ou 4511 ou 451125..." fluid></InputText>
                    </div>
                    <div class="basis-1/3">
                        <label for="libelle_cpv">Libellé CPV</label>
                        <InputText inputId="libelle_cpv" name="libelle_cpv" placeholder="Ex: ordinateur, tablette" fluid disabled></InputText>
                    </div>
                    <div class="basis-1/3">
                        <label for="lieu">Lieu</label>
                        <Select v-model="filtres.code_lieu" :options="departements" optionLabel="value" optionValue="code" inputId="lieu" name="lieu" aria-label="Sélecteur de département" placeholder="Tous les départements" showClear fluid />
                    </div>
                </div>
                <div v-if="recherche_avancee" class="flex flex-row gap-5 mb-5">
                    <div class="basis-1/3">
                        <label for="forme_prix">Forme de prix</label>
                        <Select v-model="filtres.forme_prix" :options="Object.values(FormePrix)" inputId="forme_prix" name="forme_prix" aria-label="Sélecteur de forme de prix" placeholder="Toutes" showClear fluid />
                    </div>
                    <div class="basis-1/3">
                        <label for="type_marche">Type de marché</label>
                        <Select v-model="filtres.type_marche" :options="Object.values(NatureMarche)" inputId="type_marche" name="type_marche" aria-label="Sélecteur du type de marché" placeholder="Tous" showClear fluid />
                    </div>
                    <div class="basis-1/3">
                        <label for="procedure">Procédure</label>
                        <Select v-model="filtres.procedure" :options="Object.values(ProcedureMarche)" inputId="procedure" name="procedure" aria-label="Sélecteur de la procédure utilisée" placeholder="Toutes" showClear fluid />
                    </div>
                </div>
                <div v-if="recherche_avancee" class="flex flex-row gap-5 mb-5">
                    <div class="basis-1/3">
                        <label for="categorie">Catégorie</label>
                        <Select v-model="filtres.categorie" :options="Object.values(CategorieMarche)" inputId="categorie" name="categorie" aria-label="Sélecteur de la catégorie de marché" placeholder="Toutes" showClear fluid />
                    </div>
                    <div class="basis-1/3">
                        <label for="technique_achat">Technique d'achat</label>
                        <Select
                            v-model="filtres.technique_achat"
                            :options="Object.values(TechniqueAchat)"
                            inputId="technique_achat"
                            name="technique_achat"
                            aria-label="Sélecteur de la technique d'achat utilisée"
                            placeholder="Toutes"
                            showClear
                            fluid
                        />
                    </div>
                    <div class="basis-1/3">
                        <label for="achat_durable">Achat durable</label>
                        <Select v-model="filtres.consideration" :options="options_achat_durable" inputId="achat_durable" name="achat_durable" aria-label="Sélecteur des achats durables présents" placeholder="Tous" showClear fluid />
                    </div>
                </div>
                <div v-if="recherche_avancee" class="flex flex-row gap-5 mb-5">
                    <div class="basis-1/6">
                        <label for="montant_min">Montant min</label>
                        <InputNumber v-model="filtres.montant_min" inputId="montant_min" name="montant_min" placeholder="€" fluid></InputNumber>
                    </div>
                    <div class="basis-1/6">
                        <label for="montant_max">Montant max.</label>
                        <InputNumber v-model="filtres.montant_max" inputId="montant_max" name="montant_max" placeholder="€" fluid></InputNumber>
                    </div>
                    <div class="basis-1/6">
                        <label for="duree_min">Durée min.</label>
                        <InputNumber v-model="filtres.duree_min" inputId="duree_min" name="duree_min" placeholder="mois" fluid></InputNumber>
                    </div>
                    <div class="basis-1/6">
                        <label for="duree_max">Durée max.</label>
                        <InputNumber v-model="filtres.duree_max" inputId="duree_max" name="duree_max" placeholder="mois" fluid></InputNumber>
                    </div>
                    <div class="basis-1/6">
                        <label for="date_min">Date min.</label>
                        <DatePicker v-model="filtres.date_min" inputId="date_min" name="date_min" updateModelType="date" showIcon showButtonBar fluid />
                    </div>
                    <div class="basis-1/6">
                        <label for="date_max">Date max.</label>
                        <DatePicker v-model="filtres.date_max" inputId="date_max" name="date_max" updateModelType="date" showIcon showButtonBar fluid />
                    </div>
                </div>
                <Message size="small" severity="secondary" variant="simple" class="mb-1">Cliquez sur «&nbsp;Chercher&nbsp;» pour afficher tous les marchés. Limitez la recherche en utilisant les différents filtres ci-dessus.</Message>
                <Button class="uppercase w-full" type="submit" label="Chercher" severity="primary" />
            </form>
        </Panel>

        <hr />
        <IndicateursCles v-if="marches.length" :query :dateMin="filtres.date_min" :dateMax="filtres.date_max" />
        <DistributionTemporelleMarches v-if="marches.length" :query :dateMin="filtres.date_min" :dateMax="filtres.date_max" />

        <section>
            <h2 class="title">Toutes les données de votre recherche</h2>
            <p>Ce tableau affiche les principales informations des marchés de votre sélection. Cliquez sur «&nbsp;Voir&nbsp;» pour accéder au détail de chaque marché.</p>
            <DataTable v-if="marches.length" :value="marches" size="small" stripedRows paginator :rows="10" :rowsPerPageOptions="[10, 25, 50]" :pt="{ column: { headerCell: { style: 'font-size:0.8rem; text-transform:uppercase;' } } }">
                <Column header="Détails">
                    <template #body="{ data }">
                        <Button label="Voir" aria-label="Voir les détails du marché" @click="marcheUid = data.uid" />
                    </template>
                </Column>
                <Column field="cpv" header="CPV" sortable></Column>
                <Column field="objet" header="Objet" sortable style="min-width: 20rem"></Column>
                <Column field="acheteur.nom" header="Acheteur" sortable>
                    <template #body="{ data }">{{ structureName(data.acheteur) }}</template>
                </Column>
                <Column header="Fournisseur">
                    <template #body="{ data }">
                        <div v-for="titulaire in data.titulaires" :key="titulaire.uid">
                            {{ structureName(titulaire) }}&nbsp;<span v-tooltip="getCatEntreprise(titulaire.cat_entreprise)" class="text-sm">[{{ titulaire.cat_entreprise }}]</span>
                        </div>
                    </template>
                </Column>
                <Column field="date_notification" header="Date" sortable>
                    <template #body="{ data }">
                        {{ formatDate(data.date_notification) }}
                        <br />
                        ({{ data.duree_mois }} mois)
                    </template></Column
                >
                <Column field="montant" header="Montant" dataType="numeric" sortable>
                    <template #body="{ data }">
                        {{ formatCurrency(parseFloat(data.montant)) }}
                    </template>
                    ></Column
                >
            </DataTable>
        </section>
        <ModaleMarche v-model="marcheUid" />
    </main>
</template>

<style scoped>
i {
    display: block;
    font-size: 2rem;
    font-weight: bold;
    padding-bottom: 1rem;
}
</style>
