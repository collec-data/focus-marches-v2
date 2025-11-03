import {
    CategorieMarche,
    type CategoriesDto,
    Ccag,
    type DecpMalFormeDto,
    type IndicateursDto,
    type MarcheAllegeDto,
    type MarcheCategorieDepartementDto,
    type MarcheCcagDto,
    type MarcheDepartementDto,
    type MarcheNatureDto,
    type MarcheProcedureDto,
    ProcedureMarche,
    StatsErreursDto,
    type StructureAggMarchesDto
} from '../src/client/types.gen.ts';

export const marche: MarcheAllegeDto = {
    uid: 1234,
    id: '00001234',
    acheteur: { uid: 42, identifiant: '000000', type_identifiant: 'SIRET', nom: 'Acheteur', vendeur: false, acheteur: true },
    objet: 'Lorem ipsum dolor',
    categorie: 'Services',
    cpv: '123456',
    sous_traitance_declaree: false,
    actes_sous_traitance: [],
    date_notification: new Date('2025-01-01'),
    montant: '1000',
    titulaires: [{ uid: 4321, identifiant: '00000011111', type_identifiant: 'SIRET', nom: 'Vendeur', vendeur: true, acheteur: false }],
    considerations_environnementales: [],
    considerations_sociales: []
};

export const indicateurs: IndicateursDto = { periode: null, nb_contrats: 456, montant_total: '10000000000.00', nb_acheteurs: 2, nb_fournisseurs: 3, nb_sous_traitance: 4, nb_innovant: 5 };

export const structure: StructureAggMarchesDto = { structure: { uid: 42, identifiant: '0000000', type_identifiant: 'SIRET', nom: 'Une structure', vendeur: false, acheteur: true }, montant: '10000000', nb_contrats: 500 };

export const nature: MarcheNatureDto[] = [
    { mois: '2025-01', nature: 1, montant: '100', nombre: 2 },
    { mois: '2025-02', nature: 1, montant: '200', nombre: 1 }
];

export const procedures: MarcheProcedureDto[] = [
    { procedure: ProcedureMarche.APPEL_D_OFFRES_OUVERT, montant: '100.00', nombre: 1 },
    { procedure: ProcedureMarche.APPEL_D_OFFRES_RESTREINT, montant: '200.00', nombre: 3 }
];

export const departements: MarcheDepartementDto[] = [
    { code: '35', montant: '100', nombre: 2 },
    { code: '44', montant: '200', nombre: 1 }
];

export const categories_departements: MarcheCategorieDepartementDto[] = [
    { categorie: 'Fournitures', code: '35', montant: '1000' },
    { categorie: 'Fournitures', code: '44', montant: '5000' },
    { categorie: 'Services', code: '35', montant: '6000' },
    { categorie: 'Fournitures', code: '35', montant: '900.0' },
    { categorie: 'Fournitures', code: '44', montant: '1000.0' }
];

export const erreurs: DecpMalFormeDto[] = [
    {
        uid: 123,
        decp: {},
        erreurs: [{ uid: 456, type: 'missing', localisation: '.', message: 'attribut manquant' }]
    }
];

export const erreursStats: StatsErreursDto[] = [{ erreur: 'Field required', nombre: 1263, localisation: 'offresRecues' }];

export const ccag: MarcheCcagDto[] = [{ ccag: Ccag.TRAVAUX, montant: '10000', nombre: 123, categorie: CategorieMarche.TRAVAUX }];

export const categories: CategoriesDto[] = [
    { categorie: 'Services', mois: '2020-11', montant: '123456.0', nombre: 2 },
    { categorie: 'Travaux', mois: '2020-12', montant: '654321.2', nombre: 1 },
    { categorie: 'Services', mois: '2021-01', montant: '789456.0', nombre: 2 },
    { categorie: 'Fournitures', mois: '2021-01', montant: '654789.2', nombre: 1 }
];
