import { fireEvent, render, screen, waitFor, within } from '@testing-library/vue';
import { http, HttpResponse } from 'msw';
import { beforeEach, describe, expect, it } from 'vitest';

import Recherche from '../../src/views/Recherche.vue';

import { marche } from '../api_test_data';
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

        await waitFor(() => expect(screen.getAllByText('Le nombre de résultats affichés est limité aux 5000 plus récents. Veuillez affiner vos filtres.').length).toBeGreaterThan(0));
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

    it("n'affiche aucune section avant d'avoir lancé une recherche", () => {
        const { unmount } = render(Recherche);

        expect(screen.getByText(/Lancez une recherche/)).toBeTruthy();
        expect(screen.queryByRole('heading', { name: 'Toutes les données de votre recherche' })).toBeNull();
        expect(screen.queryByRole('heading', { name: 'Distribution temporelle des marchés' })).toBeNull();
        expect(screen.queryByRole('heading', { name: 'Indicateurs clés' })).toBeNull();
        unmount();
    });

    it('affiche les trois sections une fois la recherche lancée, y compris sans résultat', async () => {
        const { container, unmount } = render(Recherche);

        await rechercher(container);

        await waitFor(() => expect(screen.getByRole('heading', { name: 'Toutes les données de votre recherche' })).toBeTruthy());
        expect(screen.getByRole('heading', { name: 'Distribution temporelle des marchés' })).toBeTruthy();
        expect(screen.getByRole('heading', { name: 'Indicateurs clés' })).toBeTruthy();
        expect(screen.queryByText(/Lancez une recherche/)).toBeNull();
        unmount();
    });

    it("ne demande les marchés qu'une fois pour le tableau et le graphique", async () => {
        let reponses = 0;
        server.use(
            http.get(base + 'marche/', () => {
                reponses += 1;
                return HttpResponse.json([marche]);
            })
        );

        const { container, unmount } = render(Recherche);
        await rechercher(container);

        await waitFor(() => expect(screen.getByText('Lorem ipsum dolor')).toBeTruthy());
        const distribution = await screen.findByRole('heading', { name: 'Distribution temporelle des marchés' });
        await waitFor(() => expect(within(distribution.closest('section') as HTMLElement).queryByLabelText('Chargement en cours')).toBeNull());
        expect(reponses).toBe(1);
        unmount();
    });

    it('donne à chaque section son propre état de chargement', async () => {
        let liberer: () => void = () => {};
        const attente = new Promise<void>((resolve) => {
            liberer = resolve;
        });
        server.use(
            http.get(base + 'marche/', async () => {
                await attente;
                return HttpResponse.json([marche]);
            })
        );

        const { container, unmount } = render(Recherche);
        await rechercher(container);

        const distribution = await waitFor(() => {
            const section = screen.getByRole('heading', { name: 'Distribution temporelle des marchés' }).closest('section');
            expect(section).not.toBeNull();
            return section as HTMLElement;
        });
        expect(within(distribution).getByLabelText('Chargement en cours')).toBeTruthy();

        const donnees = screen.getByRole('heading', { name: 'Toutes les données de votre recherche' }).closest('section') as HTMLElement;
        expect(donnees.querySelector('.p-datatable-mask')).not.toBeNull();

        // Les indicateurs ne dépendent pas des marchés : leur section n'attend pas la liste.
        await waitFor(() => expect(screen.getByText('PÉRIODE')).toBeTruthy());

        liberer();
        await waitFor(() => expect(within(donnees).getByText('Lorem ipsum dolor')).toBeTruthy());
        expect(within(distribution).queryByLabelText('Chargement en cours')).toBeNull();
        unmount();
    });
});
