<script setup lang="ts">
import { useLayout } from '@/layout/composables/layout';
import { watch } from 'vue';
import { useRoute } from 'vue-router';
import AppConfigurator from './AppConfigurator.vue';
import AppMenu from './AppMenu.vue';

const { toggleMenu, menuMobileActive, toggleDarkMode, isDarkTheme } = useLayout();

const route = useRoute();

watch(
    () => route.path,
    () => {
        if (menuMobileActive.value) toggleMenu();
    }
);
</script>

<template>
    <header class="layout-topbar">
        <div class="layout-topbar-first-container">
            <div class="layout-topbar-logo-container">
                <router-link to="/" class="layout-topbar-logo">
                    <img id="topbar_logo" src="@/assets/images/logo.png" alt="" />
                </router-link>
            </div>

            <button class="layout-topbar-menu-button layout-topbar-action" type="button" @click="toggleMenu">
                <i class="pi pi-bars"></i>
            </button>
        </div>

        <AppMenu></AppMenu>

        <div class="layout-topbar-actions">
            <div class="layout-config-menu">
                <button v-tooltip.left="'Passer au mode ' + (isDarkTheme ? 'clair' : 'sombre')" type="button" aria-label="Changer entre l'affichage clair et sombre" class="layout-topbar-action" @click="toggleDarkMode">
                    <i :class="['pi', { 'pi-moon': isDarkTheme, 'pi-sun': !isDarkTheme }]"></i>
                </button>
                <div class="relative">
                    <button
                        v-tooltip.left="'Modifier la couleur et le thème'"
                        v-styleclass="{ selector: '@next', enterFromClass: 'hidden', enterActiveClass: 'animate-scalein', leaveToClass: 'hidden', leaveActiveClass: 'animate-fadeout', hideOnOutsideClick: true }"
                        aria-label="Changer la palette de couleurs"
                        type="button"
                        class="layout-topbar-action layout-topbar-action-highlight"
                    >
                        <i class="pi pi-palette"></i>
                    </button>
                    <AppConfigurator />
                </div>
            </div>
        </div>
    </header>
</template>
