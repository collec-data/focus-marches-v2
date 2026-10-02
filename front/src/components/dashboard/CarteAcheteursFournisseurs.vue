<script setup lang="ts">
import { listAcheteurs, listVendeurs, type StructureEtendueDto } from '@/client';
import { getNow, structureName } from '@/service/HelpersService';
import { useStructureIdentifiee } from '@/service/UseStructureIdentifiee';
import { useReactiveFetch } from '@/utils/query';
import * as L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { computed, onMounted, type PropType, ref, toRaw, useId, watch } from 'vue';

// `undefined` plutôt que `null` par défaut : « acheteur demandé mais pas encore identifié » se distingue de « aucun acheteur demandé ».
const props = defineProps({
    acheteur: { type: Object as PropType<Partial<StructureEtendueDto> | null>, required: false },
    acheteurSiret: { type: String as PropType<string | null>, required: false },
    vendeur: { type: Object as PropType<Partial<StructureEtendueDto> | null>, required: false },
    dateMin: { type: Date, default: new Date(settings.date_min) },
    dateMax: { type: Date, default: getNow() }
});

const {
    uid: uidAcheteur,
    structure: acheteur,
    erreur: erreurIdentite,
    refetch: refetchIdentite
} = useStructureIdentifiee(
    () => props.acheteur?.uid,
    () => props.acheteurSiret ?? null,
    { structure: true }
);

// La carte part de l'acheteur dès qu'il est identifié ; à défaut, elle part du vendeur.
const coteAcheteur = computed(() => typeof uidAcheteur.value === 'number');

const structurePrincipale = computed<Partial<StructureEtendueDto> | null>(() => (coteAcheteur.value ? acheteur.value : (props.vendeur ?? null)));

const uidPrincipal = computed<number | null>(() => {
    if (uidAcheteur.value === undefined) {
        return null;
    }
    return coteAcheteur.value ? uidAcheteur.value : (props.vendeur?.uid ?? null);
});

const options = computed(() => {
    // Tant que l'acheteur n'est pas identifié, le risque est de cartographier tous les acheteurs de la
    // plateforme pour une structure demandée : on n'envoie rien plutôt qu'une carte fausse.
    if (uidAcheteur.value === undefined || uidPrincipal.value === null) {
        return undefined;
    }
    return {
        query: {
            acheteur_uid: coteAcheteur.value ? uidPrincipal.value : undefined,
            vendeur_uid: coteAcheteur.value ? undefined : uidPrincipal.value,
            date_debut: props.dateMin ?? undefined,
            date_fin: props.dateMax ?? undefined
        }
    };
});

const lister = (requete: NonNullable<typeof options.value>) => (coteAcheteur.value ? listVendeurs(requete) : listAcheteurs(requete));

const { etat, refetch } = useReactiveFetch(lister, options);

const items = computed(() => (etat.value.statut === 'succes' ? etat.value.data.items : []));

const mapId = useId();
const initialMap = ref<L.Map>();

let mainMarker: L.Marker | null = null;
let markers: Array<L.Marker> = [];

onMounted(() => {
    // Init map, no data set at this point
    initialMap.value = L.map(mapId).setView([46.23, 2.2], 5);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(toRaw(initialMap.value));

    const legend = L.control({ position: 'bottomleft' });
    legend.onAdd = function () {
        const div = L.DomUtil.create('div', 'lf-legend');
        div.innerHTML = '<h3>Légende :</h3><ul><li><div class="lf-vendeur-icon"></div> Fournisseur·s</li><li><div class="lf-acheteur-icon"></div> Acheteur·s</li></ul>';
        return div;
    };
    legend.addTo(initialMap.value);
});

watch(structurePrincipale, (structure) => {
    const carte = initialMap.value;
    if (!carte || !structure?.latitude) {
        return;
    }
    mainMarker?.remove();
    mainMarker = L.marker([structure.latitude, structure.longitude], { icon: L.divIcon({ className: 'lf-' + (coteAcheteur.value ? 'acheteur' : 'vendeur') + '-icon', iconSize: [30, 30] }), zIndexOffset: 10000 })
        .addTo(toRaw(carte))
        .bindPopup(structureName(structure));
});

watch(items, (liste) => {
    const carte = initialMap.value;
    if (!carte) {
        return;
    }
    const icon = L.divIcon({ className: coteAcheteur.value ? 'lf-vendeur-icon' : 'lf-acheteur-icon', iconSize: [20, 20] });
    markers.forEach((marker) => marker.remove());
    markers = [];
    for (const agrégat of liste) {
        if (agrégat.structure.latitude && agrégat.structure.longitude) {
            markers.push(L.marker([agrégat.structure.latitude, agrégat.structure.longitude], { icon: icon }).addTo(toRaw(carte)).bindPopup(structureName(agrégat.structure)));
        }
    }
});
</script>

<template>
    <section>
        <h2>La localisation des {{ coteAcheteur ? 'fournisseurs' : 'acheteurs' }}</h2>

        <ErreurChargement v-if="erreurIdentite" :erreur="erreurIdentite" message="Aucune structure ne correspond à ce SIRET" @retry="refetchIdentite" />
        <ErreurChargement v-else-if="etat.statut === 'erreur'" :erreur="etat.erreur" message="Le chargement de la carte a échoué" class="my-4" @retry="refetch" />
        <ChargementEnCours v-else-if="uidAcheteur === undefined || etat.statut !== 'succes'" class="my-4" libelle="Chargement de la carte" />

        <div :id="mapId" style="min-height: 30rem; max-width: 60rem; margin: 0 auto"></div>
        <BoutonIframe v-if="structurePrincipale?.identifiant" :path="'acheteur/' + structurePrincipale.identifiant + '/fournisseurs/carte'" name="La répartition géographique des fournisseurs" />
    </section>
</template>

<style>
.lf-vendeur-icon {
    display: inline-block;
    border-radius: 50%;
    width: 1rem;
    height: 1rem;
    border: 1px solid var(--p-gray-950);
    background-color: var(--p-red-600);
}
.lf-acheteur-icon {
    display: inline-block;
    border-radius: 50%;
    width: 1rem;
    height: 1rem;
    border: 1px solid var(--p-gray-950);
    background-color: var(--p-blue-600);
}
.lf-legend {
    border: 1px solid var(--p-gray-500);
    background-color: white;
    border-radius: 0.5rem;
    padding: 0.5rem;
}
.lf-legend h3 {
    margin: 0;
    text-align: left;
}
</style>
