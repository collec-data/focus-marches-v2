import {
    CategorieMarche,
    type CategoriesDto,
    Ccag,
    ConsiderationsSociales,
    ConsiderationsEnvironnementales,
    type ConsiderationsMensuelleDto,
    type ConsiderationsEnvDto,
    type ConsiderationsSocialeDto,
    type ConsiderationDto,
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
    type StructureAggMarchesDto,
    type ContratConcessionDto,
    type LieuDto
} from '../src/client/types.gen.ts';

export const marche: MarcheAllegeDto = {
    uid: 1234,
    id: '00001234',
    acheteur: { uid: 42, identifiant: '000000', type_identifiant: 'SIRET', nom: 'Acheteur', vendeur: false, acheteur: true, cat_entreprise: 'GE' },
    objet: 'Lorem ipsum dolor',
    categorie: 'Services',
    cpv: '123456',
    sous_traitance_declaree: false,
    actes_sous_traitance: [],
    date_notification: new Date('2025-01-01'),
    montant: '1000',
    titulaires: [{ uid: 4321, identifiant: '00000011111', type_identifiant: 'SIRET', nom: 'Vendeur', vendeur: true, acheteur: false, cat_entreprise: 'PME' }],
    considerations_environnementales: [],
    considerations_sociales: [],
    montant_max_accord_cadre: 999999
};

export const indicateurs: IndicateursDto = {
    periode: null,
    nb_contrats: 456,
    montant_total: '10000000000.00',
    nb_acheteurs: 2,
    nb_fournisseurs: 3,
    nb_sous_traitance: 4,
    nb_innovant: 5,
    nb_considerations_sociale_env: 10,
    nb_considerations_env: 16,
    nb_considerations_sociales: 20
};

export const structure: StructureAggMarchesDto = {
    structure: { uid: 42, identifiant: '0000000', type_identifiant: 'SIRET', nom: 'Une structure', vendeur: false, acheteur: true, cat_entreprise: 'ETI' },
    montant: '10000000',
    nb_contrats: 500
};

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

export const concession: ContratConcessionDto = [
    {
        uid: 10,
        id: '2025S123456',
        autorite_concedante: { uid: 42, identifiant: '123456789', type_identifiant: 'SIRET', nom: 'Autorité', vendeur: false, acheteur: true },
        nature: 'Délégation de service public',
        objet: 'Lorem ipsum dolor',
        procedure: 'Procédure négociée ouverte',
        duree_mois: 42,
        duree_mois_initiale: 40,
        date_signature: '2025-01-01',
        date_publication: '2025-01-10',
        date_debut_execution: '2025-01-30',
        valeur_globale: '1000000.00',
        valeur_globale_initiale: '900000.00',
        montant_subvention_publique: '10.0',
        donnees_execution: [],
        concessionnaires: [{ uid: 24, identifiant: '987654321', type_identifiant: 'SIRET', nom: 'Concessionnaire', vendeur: true, acheteur: false }],
        considerations_sociales: [],
        considerations_environnementales: []
    }
];

export const lieux: LieuDto[] = [
    { uid: 1, code: '35', type_code: 'Code département' },
    { uid: 2, code: '44', type_code: 'Code département' },
    { uid: 3, code: '56', type_code: 'Code département' },
    { uid: 4, code: '29', type_code: 'Code département' },
    { uid: 5, code: '22', type_code: 'Code département' }
];

export const consideration_env: ConsiderationsEnvDto[] = [
    { consideration: ConsiderationsEnvironnementales.CRITÈRE_ENVIRONNEMENTAL, nombre: 1 },
    { consideration: ConsiderationsEnvironnementales.CLAUSE_ENVIRONNEMENTALE, nombre: 2 },
    { consideration: ConsiderationsEnvironnementales.PAS_DE_CONSIDÉRATION_ENVIRONNEMENTALE, nombre: 3 }
];

export const consideration_soc: ConsiderationsSocialeDto[] = [
    { consideration: ConsiderationsSociales.CRITÈRE_SOCIAL, nombre: 1 },
    { consideration: ConsiderationsSociales.CLAUSE_SOCIALE, nombre: 2 },
    { consideration: ConsiderationsSociales.PAS_DE_CONSIDÉRATION_SOCIALE, nombre: 3 }
];

export const consideration_combine: ConsiderationDto[] = [
    { consideration: 'Clause environnementale et sociale', nombre: 1 },
    { consideration: 'Critère environnemental et social', nombre: 2 },
    { consideration: 'Pas de considérations', nombre: 3 }
];

export const considerations: ConsiderationsMensuelleDto[] = [
    {
        consideration: 'Aucune considération',
        data: [
            { nombre: 1, annee: '2024' },
            { nombre: 2, annee: '2025' }
        ]
    },
    {
        consideration: 'Considération sociale uniquement',
        data: [
            { nombre: 3, annee: '2024' },
            { nombre: 4, annee: '2025' }
        ]
    }
];
