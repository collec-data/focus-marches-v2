import { render } from '@testing-library/vue';
import { axe, toHaveNoViolations } from 'jest-axe';
import { expect, it, vi } from 'vitest';
import DetailsFournisseur from '../../src/components/DetailsFournisseur.vue';
import { StructureEtendueDto } from '../../src/client';

expect.extend(toHaveNoViolations);

it('Details fournisseurs has no accessibility violation', async () => {
    const { container, unmount } = render(DetailsFournisseur, { propsData: { vendeur: {} as StructureEtendueDto } });
    const results = await axe(container);
    expect(results).toHaveNoViolations();
    unmount();
});
