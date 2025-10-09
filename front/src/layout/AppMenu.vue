<script setup>
import { ref } from 'vue';

import AppMenuItem from './AppMenuItem.vue';

const model = ref([
    {
        items: [
            { label: 'Accueil', icon: 'pi pi-fw pi-home', to: '/' },
            { label: 'Acheteurs', icon: 'pi pi-fw pi-building', to: '/acheteurs' },
            { label: 'Fournisseurs', icon: 'pi pi-fw pi-briefcase', to: '/fournisseurs' },
            { label: 'Recherche', icon: 'pi pi-fw pi-search', to: '/recherche' },
            { label: 'Erreurs importation', icon: 'pi pi-fw pi-exclamation-triangle', to: '/erreurs-importation' }
        ]
    }
]);
</script>

<template>
    <ul class="layout-menu">
        <template v-for="(item, i) in model" :key="item">
            <AppMenuItem v-if="!item.separator" :item="item" :index="i"></AppMenuItem>
            <li v-if="item.separator" class="menu-separator"></li>
        </template>
    </ul>
</template>

<style lang="scss" scoped></style>
