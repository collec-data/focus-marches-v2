import { client } from '@/client/client.gen';
import { createApp } from 'vue';
import App from './App.vue';
import router from './router';

import Aura from '@primeuix/themes/aura';
import { fr } from 'primelocale/fr.json';
import PrimeVue from 'primevue/config';
import ConfirmationService from 'primevue/confirmationservice';
import ToastService from 'primevue/toastservice';
import Tooltip from 'primevue/tooltip';
import { loadMarkdowns } from './service/markdownsLoader';

import '@/assets/styles.scss';
import { definePreset } from '@primeuix/themes';
import { getPaletteByName } from './service/ConfiguratorService';

client.setConfig({ baseUrl: settings.api.base });

const EnvPreset = definePreset(Aura, { semantic: { primary: getPaletteByName(settings.color) } });

const app = createApp(App);

app.use(router);
app.use(PrimeVue, {
    theme: {
        preset: EnvPreset,
        options: {
            darkModeSelector: '.app-dark'
        }
    },
    locale: fr
});
app.use(ToastService);
app.use(ConfirmationService);
app.directive('tooltip', Tooltip);

app.mount('#app');

loadMarkdowns();
