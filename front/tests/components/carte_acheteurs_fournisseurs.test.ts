import { render } from '@testing-library/vue';
import { axe, toHaveNoViolations } from 'jest-axe';
import { expect, it, vi } from 'vitest';
import CarteAcheteursFournisseurs from '../../src/components/dashboard/CarteAcheteursFournisseurs.vue';

expect.extend(toHaveNoViolations);

it('Achat durable has no accessibility violation', async () => {
    const { container, unmount } = render(CarteAcheteursFournisseurs, { propsData: { acheteur: { uid: 42 } as StructureEtendueDto, dateMin: new Date('2020-01-01'), dateMax: new Date('2026-01-01') } });
    const results = await axe(container);
    expect(results).toHaveNoViolations();
    unmount();
});

it('Achat durable has no accessibility violation', async () => {
    const { container, unmount } = render(CarteAcheteursFournisseurs, { propsData: { vendeur: { uid: 42 } as StructureEtendueDto, dateMin: new Date('2020-01-01'), dateMax: new Date('2026-01-01') } });
    const results = await axe(container);
    expect(results).toHaveNoViolations();
    unmount();
});
