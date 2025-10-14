import { expect, it } from 'vitest';
import { longLabelsBreaker } from '../../src/service/HelpersService.ts';

it('break long strings', async () => {
    expect(longLabelsBreaker(['Lorem ipsum dolor', null, 'Looooooooooooooorem'], 13)).toStrictEqual(['Lorem ipsum<br>dolor', null, 'Looooooooooooooorem']);
});
