<script lang="ts" setup>
import { marked } from 'marked';

defineProps({ content: { type: String, required: true } });
</script>

<template>
    <main className="card">
        <div :class="$style.markdown_content">
            <div id="markdown_content" v-html="marked(content)"></div>
        </div>
    </main>
</template>

<style module>
.markdown_content a {
    text-decoration: underline;
    text-decoration-color: var(--p-primary-color);
    text-decoration-thickness: 0.2rem;
}
</style>
