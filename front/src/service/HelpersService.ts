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
