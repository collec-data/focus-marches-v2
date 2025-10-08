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

/**
 * Insère des retours à la ligne quand les labels sont trop longs
 * @param labels La liste de labels à modifier
 * @param length La longueur à partir de laquelle on coupe les labels
 * @returns La liste modifiée
 */
export function longLabelsBreaker(labels: Array<string | null>, length: number = 13): Array<string | null> {
    function addLineBreak(e: string, length: number): string {
        if (e && e.length > length) {
            const index = e.indexOf(' ', length);
            if (index > 1) {
                e = e.substring(0, index) + '<br>' + addLineBreak(e.substring(index), length);
            }
            return e;
        }
        return e;
    }
    return labels.map((e) => {
        return e ? addLineBreak(e, length) : e;
    });
}
