import { defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
    input: 'http://127.0.0.1:8000/openapi.json',
    output: {
        path: './src/client'
    },
    plugins: [
        {
            baseUrl: false,
            name: '@hey-api/client-fetch'
        },
        {
            dates: true,
            name: '@hey-api/transformers'
        },
        {
            name: '@hey-api/sdk',
            transformer: true
        },
        {
            name: '@hey-api/typescript',
            enums: 'javascript'
        }
    ]
});
