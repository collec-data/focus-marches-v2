import { render } from '@testing-library/vue';
import { axe, toHaveNoViolations } from 'jest-axe';
import { expect, it } from 'vitest';
import IndicateursCles from '../../src/components/dashboard/IndicateursCles.vue';

expect.extend(toHaveNoViolations);

it('indicateurs cles has no accessibility violation', async () => {
    const { container, unmount } = render(IndicateursCles, { propsData: { dateMin: new Date('2020-01-01'), dateMax: new Date('2026-01-01') } });
    const results = await axe(container);
    expect(results).toHaveNoViolations();
    unmount();
});
