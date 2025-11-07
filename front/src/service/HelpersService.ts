import type { StructureDto, StructureEtendueDto } from '@/client';

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
    if (structure.type_identifiant && structure.identifiant) {
        return structure.type_identifiant + ':' + structure.identifiant;
    }
    return '';
}
