import { render } from '@testing-library/vue';
import { axe, toHaveNoViolations } from 'jest-axe';
import { expect, it } from 'vitest';
import Top12 from '../../src/components/dashboard/Top12.vue';

expect.extend(toHaveNoViolations);

it('top12 acheteurs has no accessibility violation', async () => {
    const { container, unmount } = render(Top12, { propsData: { type: 'acheteurs', dateMin: new Date('2020-01-01'), dateMax: new Date('2026-01-01') } });
    const results = await axe(container);
    expect(results).toHaveNoViolations();
    unmount();
});

it('top12 vendeurs has no accessibility violation', async () => {
    const { container, unmount } = render(Top12, { propsData: { type: 'vendeurs', dateMin: new Date('2020-01-01'), dateMax: new Date('2026-01-01') } });
    const results = await axe(container);
    expect(results).toHaveNoViolations();
    unmount();
});
