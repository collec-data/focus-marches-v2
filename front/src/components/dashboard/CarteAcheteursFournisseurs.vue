<script setup lang="ts">
import { listAcheteurs, listVendeurs, type StructureEtendueDto } from '@/client';
import { structureName } from '@/service/HelpersService';
import * as L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { onMounted, type PropType, ref, toRaw, useId, watch, watchEffect } from 'vue';

const props = defineProps({
    acheteur: { type: Object as PropType<Partial<StructureEtendueDto>>, default: () => ({}) },
    vendeur: { type: Object as PropType<Partial<StructureEtendueDto>>, default: () => ({}) },
    dateMin: { type: Date, required: true },
    dateMax: { type: Date, required: true }
});

const acheteur = ref<Partial<StructureEtendueDto>>(props.acheteur);
const vendeur = ref<Partial<StructureEtendueDto>>(props.vendeur);

const mapId = useId();
const initialMap = ref();

let mainMarker: null | L.marker = null;
let markers: Array<L.marker> = [];

function fetchData() {
    if (acheteur.value.uid || vendeur.value.uid) {
        (acheteur.value.uid ? listVendeurs : listAcheteurs)({
            query: {
                limit: null,
                acheteur_uid: acheteur.value ? acheteur.value.uid : null,
                vendeur_uid: vendeur.value ? vendeur.value.uid : null,
                date_debut: props.dateMin,
                date_fin: props.dateMax
            }
        }).then((response) => {
            if (response.data) {
                const icon = L.divIcon({ className: acheteur.value.uid ? 'lf-vendeur-icon' : 'lf-acheteur-icon', iconSize: [20, 20] });
                markers.forEach((marker) => {
                    marker.remove();
                });
                markers = [];
                response.data.forEach((structure) => {
                    if (structure.structure.latitude && structure.structure.longitude) {
                        const coordonnees = [structure.structure.latitude, structure.structure.longitude];
                        markers.push(L.marker(coordonnees, { icon: icon }).addTo(toRaw(initialMap.value)).bindPopup(structureName(structure.structure)));
                    }
                });
            }
        });
    }
}

onMounted(() => {
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

    fetchData();
});

watch([() => props.dateMin, () => props.dateMax], () => {
    fetchData();
});

watchEffect(() => {
    acheteur.value = props.acheteur;
    if (initialMap.value && acheteur.value.latitude) {
        const coordonnees = [acheteur.value.latitude, acheteur.value.longitude];
        if (mainMarker) {
            mainMarker.remove();
        }
        mainMarker = L.marker(coordonnees, { icon: L.divIcon({ className: 'lf-acheteur-icon', iconSize: [30, 30] }), zIndexOffset: 10000 })
            .addTo(toRaw(initialMap.value))
            .bindPopup(structureName(acheteur.value));
    }
    fetchData();
});

watchEffect(() => {
    vendeur.value = props.vendeur;
    if (initialMap.value && vendeur.value.latitude) {
        const coordonnees = [vendeur.value.latitude, vendeur.value.longitude];
        if (mainMarker) {
            mainMarker.remove();
        }
        mainMarker = L.marker(coordonnees, { icon: L.divIcon({ className: 'lf-vendeur-icon', iconSize: [30, 30] }), zIndexOffset: 10000 })
            .addTo(toRaw(initialMap.value))
            .bindPopup(structureName(vendeur.value));
    }

    fetchData();
});
</script>

<template>
    <section>
        <h2>La localisation des {{ acheteur.uid ? 'fournisseurs' : 'acheteurs' }}</h2>
        <div :id="mapId" style="min-height: 30rem; max-width: 60rem; margin: 0 auto"></div>
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
