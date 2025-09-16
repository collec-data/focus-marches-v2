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
                        label: 'Crud',
                        icon: 'pi pi-fw pi-pencil',
                        to: '/pages/crud'
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
            },
            {
                label: 'UI',
                items: [
                    { label: 'Form Layout', icon: 'pi pi-fw pi-id-card', to: '/uikit/formlayout' },
                    { label: 'Input', icon: 'pi pi-fw pi-check-square', to: '/uikit/input' },
                    { label: 'Button', icon: 'pi pi-fw pi-mobile', to: '/uikit/button', class: 'rotated-icon' },
                    { label: 'Table', icon: 'pi pi-fw pi-table', to: '/uikit/table' },
                    { label: 'List', icon: 'pi pi-fw pi-list', to: '/uikit/list' },
                    { label: 'Tree', icon: 'pi pi-fw pi-share-alt', to: '/uikit/tree' },
                    { label: 'Panel', icon: 'pi pi-fw pi-tablet', to: '/uikit/panel' },
                    { label: 'Overlay', icon: 'pi pi-fw pi-clone', to: '/uikit/overlay' },
                    { label: 'Media', icon: 'pi pi-fw pi-image', to: '/uikit/media' },
                    { label: 'Menu', icon: 'pi pi-fw pi-bars', to: '/uikit/menu' },
                    { label: 'Message', icon: 'pi pi-fw pi-comment', to: '/uikit/message' },
                    { label: 'File', icon: 'pi pi-fw pi-file', to: '/uikit/file' },
                    { label: 'Chart', icon: 'pi pi-fw pi-chart-bar', to: '/uikit/charts' },
                    { label: 'Timeline', icon: 'pi pi-fw pi-calendar', to: '/uikit/timeline' },
                    { label: 'Misc', icon: 'pi pi-fw pi-circle', to: '/uikit/misc' }
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
