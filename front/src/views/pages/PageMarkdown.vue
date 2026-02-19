<script lang="ts" setup>
import { marked } from 'marked';
import { type Ref, ref, watch } from 'vue';

const props = defineProps<{ content: Ref<string | null> }>();
const html_content = ref(props.content.value);

// in case the markdown file is not downloaded at the page load, keep watching and update later
watch([() => props.content.value], () => {
    html_content.value = props.content.value;
});
</script>

<template>
    <main className="card">
        <div :class="$style.markdown_content">
            <div v-if="html_content" id="markdown_content" v-html="marked(html_content)"></div>
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
