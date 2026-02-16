declare module 'plotly.js-dist' {
    export * from 'plotly.js';
}

declare module '*.png';

type Settings = {
    api: {
        base: string;
    };
    date_min: string;
    opsn: string;
    region: string;
    departements: string;
    color: string;
};

declare var settings: Settings;
