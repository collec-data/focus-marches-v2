<script setup lang="ts">
import * as L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { onMounted, ref, toRaw, useId, watchEffect } from 'vue';
import markerImg from '../assets/images/marker-icon.png';
import markerShadow from '../assets/images/marker-shadow.png';

const props = defineProps({
    lon: { type: [Number, null] },
    lat: { type: [Number, null] },
    label: { type: [String, null] }
});

const icon = L.icon({
    iconUrl: markerImg,
    shadowUrl: markerShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    tooltipAnchor: [16, -28],
    shadowSize: [41, 41]
});

const mapId = useId();
const initialMap = ref();

watchEffect(() => {
    if (initialMap.value && props.lat && props.lon) {
        const coordonnees = [props.lat, props.lon];
        L.marker(coordonnees, { icon: icon }).addTo(toRaw(initialMap.value)).bindPopup(props.label).openPopup();
        initialMap.value.setView(coordonnees, 10);
    }
});

onMounted(() => {
    initialMap.value = L.map(mapId).setView([46.23, 2.2], 5);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(toRaw(initialMap.value));
});
</script>

<template>
    <div :id="mapId" style="min-height: 15rem"></div>
</template>
