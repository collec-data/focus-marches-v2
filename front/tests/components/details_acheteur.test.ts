import { render } from '@testing-library/vue';
import { axe, toHaveNoViolations } from 'jest-axe';
import { expect, it } from 'vitest';
import type { StructureEtendueDto } from '../../src/client';
import DetailsAcheteur from '../../src/components/DetailsAcheteur.vue';
import { mockRouter } from '../mocks.ts';

expect.extend(toHaveNoViolations);

it('details acheteur has no accessibility violation', async () => {
    await mockRouter({ uid: 42 });
    const { container, unmount } = render(DetailsAcheteur, { propsData: { acheteur: {} as StructureEtendueDto } });
    const results = await axe(container);
    expect(results).toHaveNoViolations();
    unmount();
});
