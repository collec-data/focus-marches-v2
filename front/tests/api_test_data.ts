export const marche = {
    uid: 1234,
    id: '00001234',
    acheteur: { uid: 42, identifiant: '000000', type_identifiant: 'SIRET', nom: 'Acheteur', vendeur: false, acheteur: true },
    objet: 'Lorem ipsum dolor',
    cpv: '123456',
    sous_traitance_declaree: false,
    actes_sous_traitance: [],
    date_notification: '2025-01-01',
    montant: '1000',
    titulaires: [{ uid: 4321, identifiant: '00000011111', type_identifiant: 'SIRET', nom: 'Vendeur', vendeur: true, acheteur: false }]
};

export const indicateurs = { periode: null, nb_contrats: 456, montant_total: '10000000000.00', nb_acheteurs: 2, nb_fournisseurs: 3, nb_sous_traitance: 4, nb_innovant: 5 };

export const structure = { structure: { uid: 42, identifiant: '0000000', type_identifiant: 'SIRET', nom: 'Une structure', vendeur: false, acheteur: true }, montant: '10000000', nb_contrats: 500 };

export const nature = [
    { mois: '2025-01', nature: 1, montant: '100', nombre: 2 },
    { mois: '2025-02', nature: 1, montant: '200', nombre: 1 }
];

export const procedures = [
    { procedure: 1, montant: '100.00', nombre: 1 },
    { procedure: 2, montant: '200.00', nombre: 3 }
];

export const departements = [
    { code: '35', montant: '100', nombre: 2 },
    { code: '44', montant: '200', nombre: 1 }
];

export const erreurs = [
    {
        uid: 123,
        decp: {},
        erreurs: [{ uid: 456, type: 'missing', localisation: '.', message: 'attribut manquant' }]
    }
];

export const erreursStats = [{ erreur: 'Field required', nombre: 1263, localisation: 'offresRecues' }];

export const ccag = [{ ccag: 1, montant: '10000', nombre: 123 }];
