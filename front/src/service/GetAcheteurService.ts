import { getStructureId } from '@/client';

export async function getAcheteurUid(acheteurUid: number | undefined | null, acheteurSiret: string | undefined | null): Promise<number | null> {
    if (acheteurUid && acheteurUid >= 0) {
        return acheteurUid;
    }
    if (acheteurSiret) {
        const response = await getStructureId({ path: { id: acheteurSiret, type_id: 'SIRET' } });
        if (response.data) {
            return response.data.uid;
        }
    }
    return null; // l'acheteur est en train d'être récupéré par la page acheteur, on attend. Le watch relancera fetchData
}
