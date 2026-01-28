import type { StructureDto, StructureEtendueDto } from '@/client';

export const formatNumber = (value: number) => {
    return value ? value.toLocaleString('fr-FR') : 0;
};

export const formatCurrency = (value: number) => {
    return value.toLocaleString('fr-FR', { style: 'currency', currency: 'eur' });
};

export const formatBoolean = (value: boolean) => {
    return value ? 'Oui' : 'Non';
};

export const formatDate = (value: Date) => {
    return new Date(value).toLocaleDateString('fr-FR', {
        year: 'numeric',
        month: 'numeric',
        day: 'numeric'
    });
};

export function getMonthAsString(date: Date): string {
    return date.toISOString().substring(0, 10);
}

function getLastElement(a: Array<string>): string {
    return a[a.length - 1];
}

export function breakLongLabel(label: string, max_lenght: number = 15): string {
    const result = [label];
    while (getLastElement(result).length > max_lenght && getLastElement(result).indexOf(' ') != -1) {
        const lastElement = getLastElement(result);
        const index = lastElement.lastIndexOf(' ', max_lenght);
        result[result.length - 1] = lastElement.substring(0, index);
        result.push(lastElement.substring(index + 1));
    }
    return result.join('<br>');
}

/**
 * Insère des retours à la ligne quand les labels sont trop longs
 * @param labels La liste de labels à modifier
 * @param length La longueur à partir de laquelle on coupe les labels
 * @returns La liste modifiée
 */
export function longLabelsBreaker(labels: Array<string | null>, length: number = 15): Array<string | null> {
    return labels.map((e) => {
        return e ? breakLongLabel(e, length) : e;
    });
}

export function structureName(structure: Partial<StructureDto> | Partial<StructureEtendueDto>): string {
    if (!structure) {
        return '';
    }
    if (structure.nom && structure.nom != '[ND]') {
        return structure.nom;
    }
    if (structure.type_identifiant == 'SIRET' && structure.identifiant) {
        return '[ND] SIRET' + ':' + structure.identifiant;
    }
    return structure.type_identifiant + ':' + structure.identifiant;
}

export function getNow(): Date {
    const date = new Date();
    date.setUTCHours(0, 0, 0, 0);
    return date;
}

export function getDurationInMonths(first: Date, last: Date): number {
    return (last.getFullYear() - first.getFullYear()) * 12 + (last.getMonth() - first.getMonth()) + 1;
}

export const getOpsnRegion = () => {
    return settings.opsn + ' ' + settings.region;
};

export const getCatEntreprise = (cat: string | undefined | null) => {
    switch (cat) {
        case 'GE':
            return 'GE - Grande entreprise';
        case 'PME':
            return 'PME - Petite et moyenne entreprise';
        case 'ETI':
            return 'ETI - Entreprise de taille intermédiaire';
        case 'TPE':
            return 'TPE - Très petite entreprise';
        default:
            return '-';
    }
};
