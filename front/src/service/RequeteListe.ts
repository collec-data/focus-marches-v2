import type { Options } from '@/client';
import type { RequestResult } from '@/client/client/types.gen';

/** Une page de résultats, telle qu'en renvoie un endpoint dont les données vivent côté serveur. */
export type PageListe<ITEM> = {
    items: ITEM[];
    total: number;
};

/**
 * Le client généré passe sa table de statuts à `RequestResult`, qui en extrait la charge utile : le
 * protocole d'un endpoint se décrit donc par cette table, et non par la page seule.
 */
type ReponsesListe = { 200: PageListe<unknown> };

/** Les paramètres de requête dont la table est la seule responsable, et que l'appelant n'a donc pas à fournir. */
type QueryPilotable = {
    limit?: number;
    offset?: number;
    ordre?: number;
    filtre?: string;
    /**
     * Champ de tri, laissé à `never` : la table ne connaît que des chaînes, l'endpoint son énumération de
     * champs. C'est le seul écart au protocole, et il reste du ressort de l'appelant qui pilote la table.
     */
    champs_ordre?: never;
};

/** Ce que la table demande à un endpoint de liste : une page, un tri, un terme de recherche, et ses filtres. */
type DonneesListe = {
    body?: never;
    path?: never;
    query: QueryPilotable;
    url: string;
};

/**
 * Fonction d'endpoint de liste ou de recherche du client généré.
 *
 * L'interface décrit le protocole — ce que la table demande et ce qu'elle attend en retour — sans
 * nommer l'item ni les filtres : ils sont déduits de la fonction que l'appelant passe, et le
 * compilateur vérifie alors que la table et l'endpoint parlent bien le même protocole.
 */
export type RequeteListe = (options: Options<DonneesListe, false>) => RequestResult<ReponsesListe, unknown, false, 'fields'>;

/** Les paramètres de requête déclarés par l'endpoint. */
export type QueryDe<REQUETE extends RequeteListe> = NonNullable<NonNullable<Parameters<REQUETE>[0]>['query']>;

type ClefsPilotage = 'limit' | 'offset' | 'ordre' | 'champs_ordre' | 'filtre';

/**
 * Les filtres propres à l'endpoint : tout ce que la table ne pilote pas elle-même. L'appelant n'a à
 * les fournir que si l'endpoint en attend.
 */
export type FiltresDe<REQUETE extends RequeteListe> = Omit<QueryDe<REQUETE>, ClefsPilotage>;

/** La charge utile d'un endpoint de liste, déduite de sa fonction plutôt que d'un paramètre générique. */
export type ChargeDe<REQUETE extends RequeteListe> = NonNullable<Awaited<ReturnType<REQUETE>>['data']>;

/** L'item d'une ligne de la liste. */
export type ItemDe<REQUETE extends RequeteListe> = ChargeDe<REQUETE> extends { items: (infer ITEM)[] } ? ITEM : never;

/** Les champs que l'endpoint accepte de trier, là où la table ne connaît que des chaînes. */
export type ChampTriDe<REQUETE extends RequeteListe> = QueryDe<REQUETE> extends { champs_ordre?: infer CHAMP } ? CHAMP : never;
