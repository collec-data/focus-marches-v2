import { PrimeVueResolver } from '@primevue/auto-import-resolver';
import vue from '@vitejs/plugin-vue';
import { readFileSync } from 'fs';
import { fileURLToPath, URL } from 'node:url';
import Components from 'unplugin-vue-components/vite';
import { type ConfigEnv, defineConfig, loadEnv, type Plugin } from 'vite';

const envVars = loadEnv('', globalThis.process.cwd() + '/..', '');

const API_URL = globalThis.process.env.API_URL || 'http://localhost:8000';

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
    publicDir: 'src/public',
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
    server: {
        // https://vitejs.dev/config/server-options.html#server-proxy
        proxy: {
            '/api': {
                target: API_URL,
                changeOrigin: true,
                rewrite: (path) => path.substring('/api'.length),
                configure: (proxy) => {
                    proxy.on('error', function (_err, _req, res) {
                        res.writeHead(503, {
                            'Content-Type': 'text/plain'
                        });
                        res.end('Something went wrong with api call. The back-end is unreachable');
                    });
                }
            }
        }
    },
    test: {
        environment: 'happy-dom',
        setupFiles: 'tests/setup.ts',
        coverage: {
            enabled: true,
            include: ['src/*'],
            exclude: ['src/client/', 'src/assets/', 'src/main.ts', 'src/layout/'],
            reporter: ['cobertura', 'text'],
            provider: 'istanbul',
            reportsDirectory: './coverage'
        },
        testTimeout: 40_000
    }
});
