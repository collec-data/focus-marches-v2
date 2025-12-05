import { render } from '@testing-library/vue';
import { axe, toHaveNoViolations } from 'jest-axe';
import { expect, it, vi } from 'vitest';
import CCAG from '../../src/components/dashboard/CCAG.vue';
import { mockRouter } from '../mocks.ts';

expect.extend(toHaveNoViolations);

it('CCAG has no accessibility violation', async () => {
    await mockRouter({ uid: '42' });
    const { container, unmount } = render(CCAG, { propsData: { acheteurUid: '42', dateMin: new Date('2020-01-01'), dateMax: new Date('2026-01-01') } });
    const results = await axe(container);
    expect(results).toHaveNoViolations();
    unmount();
});
