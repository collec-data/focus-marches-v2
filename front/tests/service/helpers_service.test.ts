import { expect, it } from 'vitest';
import { formatBoolean, getDurationInMonths, jourCalendaire, limiteSiTronque, getOpsnRegion, longLabelsBreaker, structureName } from '../../src/service/HelpersService.ts';

it('break long strings', async () => {
    expect(longLabelsBreaker(['Lorem ipsum dolor', null, 'Looooooooooooooorem'], 13)).toStrictEqual(['Lorem ipsum<br>dolor', null, 'Looooooooooooooorem']);
});

it('display nom structure', async () => {
    expect(structureName(null)).toStrictEqual('');
    expect(structureName({ nom: 'test' })).toStrictEqual('test');
    expect(structureName({ nom: '[ND]', identifiant: '1234', type_identifiant: 'SIRET' })).toStrictEqual('[ND] SIRET:1234');
    expect(structureName({ nom: null, identifiant: '1234', type_identifiant: 'SIRET' })).toStrictEqual('[ND] SIRET:1234');
});

it('dates diff', async () => {
    expect(getDurationInMonths(new Date(2025, 1, 1), new Date(2026, 3, 1))).toStrictEqual(15);
});

it('format boolean', async () => {
    expect(formatBoolean(true)).toStrictEqual('Oui');
    expect(formatBoolean(false)).toStrictEqual('Non');
});

it('get opsn region', async () => {
    expect(getOpsnRegion()).toStrictEqual('OPSN REGION');
});

it('jour calendaire : minuit local devient minuit UTC du même jour', async () => {
    expect(jourCalendaire(new Date(2026, 10, 7, 0, 0, 0)).toISOString()).toStrictEqual('2026-11-07T00:00:00.000Z');
    expect(jourCalendaire(new Date(2026, 10, 7, 18, 30)).toISOString()).toStrictEqual('2026-11-07T00:00:00.000Z');
});

it('limite si tronqué : seulement quand les résultats sont tronqués', async () => {
    expect(limiteSiTronque(new Headers({ 'X-Resultats-Tronques': 'true', 'X-Limite': '5000' }))).toBe(5000);
    expect(limiteSiTronque(new Headers({ 'X-Resultats-Tronques': 'false', 'X-Limite': '5000' }))).toBeNull();
    expect(limiteSiTronque(new Headers())).toBeNull();
    expect(limiteSiTronque(undefined)).toBeNull();
});
