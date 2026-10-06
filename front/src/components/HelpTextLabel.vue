<script setup lang="ts">
import { ref, useTemplateRef } from 'vue';
import Popover from 'primevue/popover';

defineProps<{
    inputId: string;
    label: string;
    help?: string;
}>();

defineSlots<{
    default(): any;
}>();

const popover = useTemplateRef('popover');
const visible = ref(false);
</script>

<template>
    <div class="flex items-center gap-2">
        <label :for="inputId" class="font-medium">{{ label }}</label>

        <button
            type="button"
            class="inline-flex items-center justify-center rounded-full text-surface-500 hover:text-primary focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary cursor-pointer"
            aria-label="Plus d'informations"
            aria-haspopup="dialog"
            :aria-expanded="visible"
            @click="popover?.toggle($event)"
        >
            <i class="pi pi-info-circle text-sm" aria-hidden="true" />
        </button>

        <Popover
            ref="popover"
            :pt="{
                root: '!bg-surface-900 !text-surface-0 !rounded-md !shadow-lg max-w-xs before:!hidden after:!hidden',
                content: '!px-3 !py-2 !text-base'
            }"
            @show="visible = true"
            @hide="visible = false"
        >
            <slot>{{ help }}</slot>
        </Popover>
    </div>
</template>
