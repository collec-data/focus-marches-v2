import { delaiDebounce, useEcritureDebouncee } from '../../src/service/Debouncer';
import { render } from '@testing-library/vue';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { defineComponent, h, nextTick, ref } from 'vue';
import type { Ref } from 'vue';

// Seuls les minuteurs sont simifiés, et restaurés après chaque test : les autres tests de la suite
// comptent sur des horloges réelles.
const minuteurs = { toFake: ['setTimeout', 'clearTimeout'] } as const;

afterEach(() => vi.useRealTimers());

/** Montre le hook dans un composant, afin que son watcher soit rattaché au cycle de vie. */
function monter(source: Ref<string>, cible: Ref<string>, surEcriture?: () => void) {
    const Composant = defineComponent({
        setup() {
            useEcritureDebouncee(source, cible, surEcriture);
            return () => h('div');
        }
    });

    const { unmount } = render(Composant);
    return { unmount };
}

async function ecrire(source: Ref<string>, valeur: string) {
    source.value = valeur;
    await nextTick();
}

describe('useEcritureDebouncee', () => {
    it("n'écrit dans la cible qu'une fois le délai écoulé", async () => {
        vi.useFakeTimers(minuteurs);
        const saisie = ref('');
        const cible = ref('');
        const { unmount } = monter(saisie, cible);

        await ecrire(saisie, 'somme');
        vi.advanceTimersByTime(delaiDebounce - 1);
        expect(cible.value).toBe('');

        vi.advanceTimersByTime(1);
        expect(cible.value).toBe('somme');

        unmount();
    });

    it('ne garde que la dernière frappe', async () => {
        vi.useFakeTimers(minuteurs);
        const saisie = ref('');
        const cible = ref('');
        const { unmount } = monter(saisie, cible);

        await ecrire(saisie, 's');
        vi.advanceTimersByTime(delaiDebounce - 1);
        await ecrire(saisie, 'so');
        vi.advanceTimersByTime(delaiDebounce - 1);
        await ecrire(saisie, 'som');
        vi.advanceTimersByTime(delaiDebounce);

        expect(cible.value).toBe('som');

        unmount();
    });

    it("signale le changement à l'appelant", async () => {
        vi.useFakeTimers(minuteurs);
        const saisie = ref('');
        const cible = ref('');
        const surEcriture = vi.fn();
        const { unmount } = monter(saisie, cible, surEcriture);

        await ecrire(saisie, 'somme');
        vi.advanceTimersByTime(delaiDebounce);

        expect(surEcriture).toHaveBeenCalledTimes(1);

        unmount();
    });
});
