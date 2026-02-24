import { render } from '@testing-library/vue';
import { axe, toHaveNoViolations } from 'jest-axe';
import { expect, it } from 'vitest';
import FiltreDates from '../../src/components/FiltreDates.vue';

expect.extend(toHaveNoViolations);

it('Filtre dates has no accessibility violation', async () => {
    const { container, unmount } = render(FiltreDates, { propsData: { dateMin: new Date('2020-01-01'), dateMax: new Date('2026-01-01') } });
    const results = await axe(container);
    expect(results).toHaveNoViolations();
    unmount();
});
