import { render } from '@testing-library/vue';
import { axe, toHaveNoViolations } from 'jest-axe';
import { expect, it, vi } from 'vitest';
import ListeMarches from '../../src/components/ListeMarches.vue';
import { mockRouter } from '../mocks.ts';

expect.extend(toHaveNoViolations);

it('liste marchés has no accessibility violation', async () => {
    await mockRouter({ uid: '42' });
    const { container, unmount } = render(ListeMarches, { propsData: { acheteurUid: '42', dateMin: new Date('2020-01-01'), dateMax: new Date('2026-01-01') } });
    const results = await axe(container);
    expect(results).toHaveNoViolations();
    unmount();
});
