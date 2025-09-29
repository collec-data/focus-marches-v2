<script setup>
import { ref } from 'vue';

import AppMenuItem from './AppMenuItem.vue';

const model = ref([
    {
        items: [
            { label: 'Accueil', icon: 'pi pi-fw pi-home', to: '/' },
            { label: 'Acheteurs', icon: 'pi pi-fw pi-building', to: '/acheteurs' },
            { label: 'Fournisseurs', icon: 'pi pi-fw pi-briefcase', to: '/fournisseurs' },
            { label: 'Recherche', icon: 'pi pi-fw pi-search', to: '/recherche' }
        ]
    },

    {
        label: 'Exemples',
        items: [
            {
                label: 'Pages',
                items: [
                    {
                        label: 'Landing',
                        icon: 'pi pi-fw pi-globe',
                        to: '/landing'
                    },
                    {
                        label: 'Not Found',
                        icon: 'pi pi-fw pi-exclamation-circle',
                        to: '/pages/notfound'
                    },
                    {
                        label: 'Empty',
                        icon: 'pi pi-fw pi-circle-off',
                        to: '/pages/empty'
                    }
                ]
            }
        ]
    }
]);
</script>

<template>
    <ul class="layout-menu">
        <template v-for="(item, i) in model" :key="item">
            <app-menu-item v-if="!item.separator" :item="item" :index="i"></app-menu-item>
            <li v-if="item.separator" class="menu-separator"></li>
        </template>
    </ul>
</template>

<style lang="scss" scoped></style>
