<script setup lang="ts">
import { useLayout } from '@/layout/composables/layout';
import { computed, ref, watch } from 'vue';
import AppFooter from './AppFooter.vue';
import AppTopbar from './AppTopbar.vue';

const { menuMobileActive, isSidebarActive } = useLayout();

const containerClass = computed(() => {
    return {
        'layout-static': true,
        'layout-mobile-active': menuMobileActive.value
    };
});

const outsideClickListener = ref<((this: Document, ev: PointerEvent) => any) | null>(null);

watch(isSidebarActive, (newVal) => {
    if (newVal) {
        bindOutsideClickListener();
    } else {
        unbindOutsideClickListener();
    }
});

function bindOutsideClickListener() {
    if (!outsideClickListener.value) {
        outsideClickListener.value = (event) => {
            if (isOutsideClicked(event)) {
                menuMobileActive.value = false;
            }
        };
        document.addEventListener('click', outsideClickListener.value);
    }
}

function unbindOutsideClickListener() {
    if (outsideClickListener.value) {
        document.removeEventListener('click', outsideClickListener.value);
        outsideClickListener.value = null;
    }
}

function isOutsideClicked(event) {
    const topbarEl = document.querySelector('.layout-topbar');

    return !topbarEl || !(topbarEl.isSameNode(event.target) || topbarEl.contains(event.target));
}
</script>

<template>
    <div class="layout-wrapper" :class="containerClass">
        <AppTopbar></AppTopbar>
        <div class="layout-main-container">
            <div class="layout-main">
                <router-view></router-view>
            </div>
            <AppFooter></AppFooter>
        </div>
        <div class="layout-mask animate-fadein"></div>
    </div>
    <Toast />
</template>
