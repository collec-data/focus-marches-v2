import { ref } from 'vue';

export const apropos = ref<string | null>(null);
export const mentions_legales = ref<string | null>(null);

async function loadAPropos() {
    apropos.value = await (await fetch('/apropos.md')).text();
}

async function loadMentionsLegales() {
    mentions_legales.value = await (await fetch(settings.mentions_legales || '/mentions-legales.md')).text();
}

export function loadMarkdowns() {
    loadAPropos();
    loadMentionsLegales();
}
