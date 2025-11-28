import { PrimeVueResolver } from '@primevue/auto-import-resolver';
import vue from '@vitejs/plugin-vue';
import { readFileSync } from 'fs';
import { fileURLToPath, URL } from 'node:url';
import Components from 'unplugin-vue-components/vite';
import { type ConfigEnv, defineConfig, loadEnv, type Plugin } from 'vite';

const envVars = loadEnv('', globalThis.process.cwd() + '/..', '');
const pluginSettingsTemplating = (templatePath: string): Plugin => {
    let config: ConfigEnv;

    return {
        name: 'settings-templating',
        configResolved: (resolvedConfig) => {
            config = resolvedConfig;
        },
        transformIndexHtml: (html) => {
            if (config.mode === 'development') {
                const template = ('' + readFileSync(templatePath)) as any;

                const settings = template.replaceAll(/\$\{([^}]+)\}/g, (_, v) => {
                    if (envVars[v] == null) {
                        throw new Error(`settings.js.template: Variable d'environnement ${v} non définie`);
                    }
                    return envVars[v];
                });

                return html.replace('<script src="/settings.js"></script>', `<script>${settings}</script>`);
            }
        },
        handleHotUpdate: ({ file, server }) => {
            if (file === `${globalThis.process.cwd()}/${templatePath}`) {
                server.ws.send({ type: 'full-reload' });
            }
        }
    };
};

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [
        vue(),
        pluginSettingsTemplating('docker/settings.js.template'),
        Components({
            resolvers: [PrimeVueResolver()]
        })
    ],
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url))
        }
    },
    css: {
        preprocessorOptions: {
            scss: {
                api: 'modern'
            }
        }
    },
    test: {
        environment: 'happy-dom',
        setupFiles: 'tests/setup.ts',
        coverage: {
            enabled: true,
            include: ['src/*'],
            exclude: ['src/client/', 'src/assets/'],
            reporter: ['cobertura', 'text'],
            provider: 'istanbul',
            reportsDirectory: './coverage'
        },
        testTimeout: 30_000
    }
});
