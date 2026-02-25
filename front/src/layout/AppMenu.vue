<script setup>
import { ref } from 'vue';

const items = ref([
    { label: 'Accueil', icon: 'pi pi-fw pi-home', to: '/' },
    { label: 'Acheteurs', icon: 'pi pi-fw pi-building', to: '/acheteurs' },
    { label: 'Fournisseurs', icon: 'pi pi-fw pi-briefcase', to: '/fournisseurs' },
    { label: 'Recherche', icon: 'pi pi-fw pi-search', to: '/recherche' }
]);
</script>

<template>
    <nav aria-label="Menu">
        <ul class="layout-menu">
            <li v-for="item in items" :key="item.label" class="layout-menu-item">
                <router-link :to="item.to" @click="itemClick($event, item, index)">
                    <i :class="item.icon" class="layout-menuitem-icon"></i>
                    <span class="layout-menuitem-text">{{ item.label }}</span>
                </router-link>
            </li>
        </ul>
    </nav>
</template>
