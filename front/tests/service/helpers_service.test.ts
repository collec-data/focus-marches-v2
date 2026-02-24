import { expect, it } from 'vitest';
import { formatBoolean, getDurationInMonths, getOpsnRegion, longLabelsBreaker, structureName } from '../../src/service/HelpersService.ts';

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
