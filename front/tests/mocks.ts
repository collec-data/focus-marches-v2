import type { MarcheAllegeDto } from '../src/client';
import type { MarchesPerimetre } from '../src/service/UseMarchesPerimetre';

export async function mockRouter(params: any): Promise<void> {
    const VueRouter = await import('vue-router');
    VueRouter.useRoute.mockReturnValue({
        params: params,
        path: '/lorem/ipsum/dolor',
        query: {}
    });
}

/** Des marchés déjà chargés, tels que les reçoit un composant d'affichage. */
export function marchesCharges(data: MarcheAllegeDto[], entetes: Record<string, string> = {}): MarchesPerimetre {
    return { etat: { statut: 'succes', data, erreur: null, entetes: new Headers(entetes) }, erreurIdentite: null, refetch: () => {}, refetchIdentite: () => {} };
}
