import pluginJs from '@eslint/js';
import prettierConfig from 'eslint-config-prettier/flat';
import pluginVue from 'eslint-plugin-vue';
import globals from 'globals';
import tseslint from 'typescript-eslint';
import pluginVueA11y from 'eslint-plugin-vuejs-accessibility';

export default [
    {
        ignores: ['dist/', 'tests/', 'postcss.config.js', 'src/client/', '**/*.d.ts', '*.config.ts', '*.config.mjs']
    },
    {
        files: ['**/*.{js,mjs,cjs,ts,vue}']
    },
    {
        languageOptions: { globals: globals.browser }
    },
    pluginJs.configs.recommended,
    ...tseslint.configs.recommended,
    ...pluginVue.configs['flat/recommended'],
    ...pluginVueA11y.configs['flat/recommended'],
    {
        rules: {
            // https://typescript-eslint.io/troubleshooting/faqs/eslint/#i-get-errors-from-the-no-undef-rule-about-global-variables-not-being-defined-even-though-there-are-no-typescript-errors
            'no-undef': 'off',

            // voir https://eslint.vuejs.org/rules pour le détail des règles
            'vue/attribute-hyphenation': ['error', 'never'],
            'vue/component-name-in-template-casing': 'error',
            'vue/custom-event-name-casing': ['error', 'camelCase'],
            'vue/define-emits-declaration': ['error', 'type-literal'],
            'vue/html-button-has-type': 'error',
            'vue/multi-word-component-names': 'off',
            //'vue/no-undef-components': 'error', // non utilisable avec auto-import-resolver
            'vue/no-unused-emit-declarations': 'error',
            'vue/no-useless-v-bind': 'error',
            'vue/prefer-true-attribute-shorthand': 'error',
            'vue/prefer-use-template-ref': 'error',
            'vue/require-default-prop': 'off',
            'vue/require-explicit-slots': 'error',
            'vue/require-macro-variable-name': 'error',
            'vue/v-for-delimiter-style': 'error',
            'vue/v-on-event-hyphenation': ['error', 'never', { autofix: true }],
            'vue/attributes-order': 'error',

            '@typescript-eslint/consistent-type-imports': ['error', { prefer: 'type-imports', fixStyle: 'separate-type-imports' }],
            '@typescript-eslint/no-explicit-any': 'off',
            'vuejs-accessibility/label-has-for': ['error', { required: { some: ['nesting', 'id'] } }]
        }
    },
    {
        files: ['**/*.vue'],
        languageOptions: {
            parserOptions: {
                parser: tseslint.parser
            }
        }
    },
    prettierConfig
];
