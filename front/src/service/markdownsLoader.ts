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
    // Ces fichiers sont statiques : un échec ici ne concerne pas les données de la plateforme, mais il ne
    // doit pas non plus remonter en rejet de promesse non traité depuis l'amorçage de l'application.
    loadAPropos().catch((raison) => console.error("Le document « à propos » n'a pas pu être chargé", raison));
    loadMentionsLegales().catch((raison) => console.error('Les mentions légales n’ont pas pu être chargées', raison));
}
