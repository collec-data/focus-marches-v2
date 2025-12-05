import { render } from '@testing-library/vue';
import { axe, toHaveNoViolations } from 'jest-axe';
import { expect, it, vi } from 'vitest';
import CategoriePrincipaleDAchat from '../../src/components/dashboard/CategoriePrincipaleDAchat.vue';

expect.extend(toHaveNoViolations);

it("categorie principale d'achat has no accessibility violation", async () => {
    const { container, unmount } = render(CategoriePrincipaleDAchat, { propsData: { dateMin: new Date('2020-01-01'), dateMax: new Date('2026-01-01') } });
    const results = await axe(container);
    expect(results).toHaveNoViolations();
    unmount();
});
