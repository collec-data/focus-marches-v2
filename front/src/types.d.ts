declare module 'plotly.js-dist' {
    export * from 'plotly.js';
}

declare module '*.png';

type Settings = {
    api: {
        base: string;
    };
};

declare var settings: Settings;
