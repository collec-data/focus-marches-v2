import { fireEvent, render, screen, waitFor } from '@testing-library/vue';
import { http, HttpResponse } from 'msw';
import { beforeEach, describe, expect, it } from 'vitest';

import Recherche from '../../src/views/Recherche.vue';

import { server } from '../setup';

const base = 'http://localhost:3000/';

let requetesMarches = 0;
let derniersFiltres = new URLSearchParams();

beforeEach(() => {
    requetesMarches = 0;
    derniersFiltres = new URLSearchParams();
    server.use(
        http.get(base + 'marche/', ({ request }) => {
            requetesMarches += 1;
            derniersFiltres = new URL(request.url).searchParams;
            return HttpResponse.json([]);
        })
    );
});

function champObjet(container: Element): HTMLInputElement {
    const champ = container.querySelector<HTMLInputElement>('input[name="objet"]');
    if (!champ) {
        throw new Error("le champ « objet » n'est pas rendu");
    }
    return champ;
}

function rechercher(container: Element) {
    const formulaire = container.querySelector('form');
    if (!formulaire) {
        throw new Error("le formulaire de recherche n'est pas rendu");
    }
    return fireEvent.submit(formulaire);
}

describe('Recherche.vue', () => {
    it("n'interroge pas les marchés avant d'avoir lancé une recherche", async () => {
        const { container, unmount } = render(Recherche);

        // La page se charge sans rien demander sur les marchés : aucun résultat n'est encore affiché.
        expect(requetesMarches).toBe(0);
        expect(screen.getByText(/Lancez une recherche/)).toBeTruthy();

        await rechercher(container);
        await waitFor(() => expect(requetesMarches).toBe(1));
        unmount();
    });

    it('relance la recherche au clic, et pas pendant la saisie', async () => {
        const { container, unmount } = render(Recherche);

        await rechercher(container);
        await waitFor(() => expect(requetesMarches).toBe(1));

        // Retoucher un filtre ne change rien : les résultats affichés restent ceux de la recherche lancée.
        await fireEvent.update(champObjet(container), 'ordinateur');
        expect(requetesMarches).toBe(1);

        await rechercher(container);
        await waitFor(() => expect(requetesMarches).toBe(2));
        expect(derniersFiltres.get('objet')).toBe('ordinateur');
        unmount();
    });

    it('affiche une erreur récupérable quand la recherche échoue', async () => {
        server.use(http.get(base + 'marche/', () => new HttpResponse(null, { status: 500 })));

        const { container, unmount } = render(Recherche);

        await rechercher(container);

        await waitFor(() => expect(screen.getByText(/Le chargement des marchés a échoué/)).toBeTruthy());
        unmount();
    });

    it("avertit que les résultats sont limités quand l'API a tronqué la réponse", async () => {
        const entetes = { 'X-Resultats-Tronques': 'true', 'X-Limite': '5000' };
        server.use(http.get(base + 'marche/', () => HttpResponse.json([], { headers: entetes })));

        const { container, unmount } = render(Recherche);
        expect(screen.queryByText(/limité aux/)).toBeNull();

        await rechercher(container);

        await waitFor(() => expect(screen.getByText('Le nombre de résultats affichés est limité aux 5000 plus récents. Veuillez affiner vos filtres.')).toBeTruthy());
        unmount();
    });

    it("n'avertit pas quand la limite n'est pas atteinte", async () => {
        let reponses = 0;
        server.use(
            http.get(base + 'marche/', () => {
                reponses += 1;
                return HttpResponse.json([], { headers: { 'X-Resultats-Tronques': 'false', 'X-Limite': '5000' } });
            })
        );

        const { container, unmount } = render(Recherche);
        await rechercher(container);

        await waitFor(() => expect(reponses).toBe(1));
        await waitFor(() => expect(screen.queryByText(/Lancez une recherche/)).toBeNull());
        expect(screen.queryByText(/limité aux/)).toBeNull();
        unmount();
    });
});
