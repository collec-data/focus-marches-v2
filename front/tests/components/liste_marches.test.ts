import { render } from '@testing-library/vue';
import { axe, toHaveNoViolations } from 'jest-axe';
import { expect, it } from 'vitest';
import ListeMarches from '../../src/components/ListeMarches.vue';
import { marche } from '../api_test_data';
import { marchesCharges, mockRouter } from '../mocks.ts';

expect.extend(toHaveNoViolations);

it('liste marchés has no accessibility violation', async () => {
    await mockRouter({ uid: 42 });
    const { container, unmount } = render(ListeMarches, { propsData: { marches: marchesCharges([marche]), acheteurUid: 42 } });
    const results = await axe(container);
    expect(results).toHaveNoViolations();
    unmount();
});
