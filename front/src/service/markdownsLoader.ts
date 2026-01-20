export let apropos: string;
export let mentions_legales: string;

async function loadAPropos() {
    apropos = await (await fetch('/apropos.md')).text();
}

async function loadMentionsLegales() {
    mentions_legales = await (await fetch('/mentions-legales.md')).text();
}

export function loadMarkdowns() {
    loadAPropos();
    loadMentionsLegales();
}
