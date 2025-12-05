import { config, RouterLinkStub } from '@vue/test-utils';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { defaultOptions } from 'primevue/config';
import { afterAll, afterEach, beforeAll, vi } from 'vitest';
import {
    ccag,
    considerations,
    consideration_combine,
    consideration_env,
    consideration_soc,
    departements,
    erreurs,
    erreursStats,
    indicateurs,
    marche,
    nature,
    procedures,
    structure,
    categories_departements,
    categories,
    concession,
    lieux
} from './api_test_data';

config.global.mocks['$primevue'] = {
    config: defaultOptions
};
config.global.stubs = {
    RouterLink: RouterLinkStub
};

vi.stubGlobal('settings', { date_min: new Date('2020-01-01'), opsn: 'OPSN', region: 'REGION' });

vi.mock('vue-router');

const baseUrl = 'http://localhost:3000/';

export const restHandlers = [
    http.get(baseUrl + 'marche/indicateurs', () => {
        return HttpResponse.json(indicateurs);
    }),
    http.get(baseUrl + 'structure/acheteur', () => {
        return HttpResponse.json([structure]);
    }),
    http.get(baseUrl + 'structure/vendeur', () => {
        return HttpResponse.json([structure]);
    }),
    http.get(baseUrl + 'structure/42', () => {
        return HttpResponse.json(structure);
    }),
    http.get(baseUrl + 'marche/', () => {
        return HttpResponse.json([marche]);
    }),
    http.get(baseUrl + 'marche/nature', () => {
        return HttpResponse.json(nature);
    }),
    http.get(baseUrl + 'marche/procedure', () => {
        return HttpResponse.json(procedures);
    }),
    http.get(baseUrl + 'marche/departement', () => {
        return HttpResponse.json(departements);
    }),
    http.get(baseUrl + 'marche/categorie-departement', () => {
        return HttpResponse.json(categories_departements);
    }),
    http.get(baseUrl + 'marche/ccag', () => {
        return HttpResponse.json(ccag);
    }),
    http.get(baseUrl + 'marche/categorie', () => {
        return HttpResponse.json(categories);
    }),
    http.get(baseUrl + 'marche/consideration', () => {
        return HttpResponse.json(considerations);
    }),
    http.get(baseUrl + 'marche/consideration/environnementale', () => {
        return HttpResponse.json(consideration_env);
    }),
    http.get(baseUrl + 'marche/consideration/sociale', () => {
        return HttpResponse.json(consideration_soc);
    }),
    http.get(baseUrl + 'marche/consideration/combine', () => {
        return HttpResponse.json(consideration_combine);
    }),
    http.get(baseUrl + 'erreurs-import', () => {
        return HttpResponse.json(erreurs);
    }),
    http.get(baseUrl + 'erreurs-import/stats', () => {
        return HttpResponse.json(erreursStats);
    }),
    http.get(baseUrl + 'contrat-concession', () => {
        return HttpResponse.json([concession]);
    }),
    http.get(baseUrl + 'lieu', () => {
        return HttpResponse.json(lieux);
    })
];

const server = setupServer(...restHandlers);

// Start server before all tests
beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));

// Close server after all tests
afterAll(() => server.close());

// Reset handlers after each test for test isolation
afterEach(() => server.resetHandlers());
