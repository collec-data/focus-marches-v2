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
export function longLabelsBreaker(labels: Array<string | null>, length: number = 15): Array<string | null> {
    function getLastElement(a: Array<string>): string {
        return a[a.length - 1];
    }

    function addLineBreak(e: string, length: number): string {
        const result = [e];
        while (getLastElement(result).length > length && getLastElement(result).indexOf(' ') != -1) {
            const lastElement = getLastElement(result);
            const index = lastElement.lastIndexOf(' ', length);
            result[result.length - 1] = lastElement.substring(0, index);
            result.push(lastElement.substring(index + 1));
        }
        return result.join('<br>');
    }
    return labels.map((e) => {
        return e ? addLineBreak(e, length) : e;
    });
}
