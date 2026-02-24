import { render } from '@testing-library/vue';
import { axe, toHaveNoViolations } from 'jest-axe';
import { expect, it } from 'vitest';
import Departements from '../../src/components/dashboard/Departements.vue';

expect.extend(toHaveNoViolations);

it('departements has no accessibility violation', async () => {
    const { container, unmount } = render(Departements, { propsData: { dateMin: new Date('2020-01-01'), dateMax: new Date('2026-01-01') } });
    const results = await axe(container);
    expect(results).toHaveNoViolations();
    unmount();
});
