import { render } from '@testing-library/vue';
import { axe, toHaveNoViolations } from 'jest-axe';
import { expect, it } from 'vitest';
import type { StructureEtendueDto } from '../../src/client';
import DetailsFournisseur from '../../src/components/DetailsFournisseur.vue';

expect.extend(toHaveNoViolations);

it('Details fournisseurs has no accessibility violation', async () => {
    const { container, unmount } = render(DetailsFournisseur, { propsData: { vendeur: {} as StructureEtendueDto } });
    const results = await axe(container);
    expect(results).toHaveNoViolations();
    unmount();
});
