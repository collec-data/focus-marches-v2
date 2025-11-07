import { expect, it } from 'vitest';
import { longLabelsBreaker, structureName } from '../../src/service/HelpersService.ts';

it('break long strings', async () => {
    expect(longLabelsBreaker(['Lorem ipsum dolor', null, 'Looooooooooooooorem'], 13)).toStrictEqual(['Lorem ipsum<br>dolor', null, 'Looooooooooooooorem']);
});

it('display nom structure', async () => {
    expect(structureName(null)).toStrictEqual('');
    expect(structureName({ nom: 'test' })).toStrictEqual('test');
    expect(structureName({ nom: '[ND]', identifiant: '1234', type_identifiant: 'SIRET' })).toStrictEqual('SIRET:1234');
    expect(structureName({ nom: null, identifiant: '1234', type_identifiant: 'SIRET' })).toStrictEqual('SIRET:1234');
    expect(structureName({ nom: null, identifiant: null, type_identifiant: null })).toStrictEqual('');
});
