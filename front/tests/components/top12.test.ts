import { render, screen } from '@testing-library/vue';
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

it('top12 affiche le classement dès que la requête « tous les marchés » a réussi', async () => {
    const { unmount } = render(Top12, { propsData: { type: 'acheteurs', dateMin: new Date('2020-01-01'), dateMax: new Date('2026-01-01') } });
    expect((await screen.findAllByText('Une structure')).length).toBeGreaterThan(0);
    expect(screen.getByRole('tab', { name: 'Tous les marchés' })).toBeTruthy();
    unmount();
});
