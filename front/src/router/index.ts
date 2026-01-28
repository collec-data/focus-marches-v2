import AppLayout from '@/layout/AppLayout.vue';
import WidgetLayout from '@/layout/WidgetLayout.vue';
import { apropos, mentions_legales } from '@/service/markdownsLoader';
import { createRouter, createWebHistory } from 'vue-router';

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/',
            component: AppLayout,
            children: [
                {
                    path: '/',
                    name: 'accueil',
                    component: () => import('@/views/Accueil.vue')
                },
                {
                    path: '/acheteurs',
                    name: 'acheteurs',
                    component: () => import('@/views/Acheteurs.vue')
                },
                {
                    path: '/acheteur/:uid',
                    name: 'acheteur',
                    component: () => import('@/views/Acheteur.vue')
                },
                {
                    path: '/fournisseurs',
                    name: 'fournisseurs',
                    component: () => import('@/views/Fournisseurs.vue')
                },
                {
                    path: '/fournisseur/:uid',
                    name: 'fournisseur',
                    component: () => import('@/views/Fournisseur.vue')
                },
                {
                    path: '/recherche',
                    name: 'recherche',
                    component: () => import('@/views/Recherche.vue')
                },
                {
                    path: 'erreurs-importation',
                    name: "Erreur à l'importation",
                    component: () => import('@/views/ErreursImportations.vue')
                },
                {
                    path: '/a-propos',
                    name: 'a propos',
                    props: () => ({ content: apropos }),
                    component: () => import('@/views/pages/PageMarkdown.vue')
                },
                {
                    path: '/mentions-legales',
                    name: 'mentions legales',
                    props: () => ({ content: mentions_legales }),
                    component: () => import('@/views/pages/PageMarkdown.vue')
                }
            ]
        },
        {
            path: '/widget/',
            component: WidgetLayout,
            props: {},
            children: [
                {
                    path: 'acheteur/:siret',
                    component: () => import('@/views/Acheteur.vue'),
                    props: (route) => ({
                        siret: route.params.siret
                    })
                },
                {
                    path: 'acheteur/:siret/details',
                    component: () => import('@/components/DetailsAcheteur.vue'),
                    props: (route) => ({
                        acheteurSiret: route.params.siret
                    })
                },
                {
                    path: 'acheteur/:siret/indicateurs',
                    component: () => import('@/components/dashboard/IndicateursCles.vue'),
                    props: (route) => ({
                        acheteurSiret: route.params.siret,
                        dateMin: route.query.dateMin,
                        dateMax: route.query.dateMax
                    })
                },
                {
                    path: 'acheteur/:siret/marches',
                    component: () => import('@/components/ListeMarches.vue'),
                    props: (route) => ({
                        acheteurSiret: route.params.siret,
                        dateMin: route.query.dateMin,
                        dateMax: route.query.dateMax
                    })
                },
                {
                    path: 'acheteur/:siret/marches/distribution',
                    component: () => import('@/components/dashboard/DistributionTemporelleMarches.vue'),
                    props: (route) => ({
                        acheteurSiret: route.params.siret,
                        dateMin: route.query.dateMin,
                        dateMax: route.query.dateMax
                    })
                },
                {
                    path: 'acheteur/:siret/marches/nature',
                    component: () => import('@/components/dashboard/NatureContrats.vue'),
                    props: (route) => ({
                        acheteurSiret: route.params.siret,
                        dateMin: route.query.dateMin,
                        dateMax: route.query.dateMax
                    })
                },
                {
                    path: 'acheteur/:siret/marches/procedure',
                    component: () => import('@/components/dashboard/Procedure.vue'),
                    props: (route) => ({
                        acheteurSiret: route.params.siret,
                        dateMin: route.query.dateMin,
                        dateMax: route.query.dateMax
                    })
                },
                {
                    path: 'acheteur/:siret/marches/ccag',
                    component: () => import('@/components/dashboard/CCAG.vue'),
                    props: (route) => ({
                        acheteurSiret: route.params.siret,
                        dateMin: route.query.dateMin,
                        dateMax: route.query.dateMax
                    })
                },
                {
                    path: 'acheteur/:siret/marches/categorie',
                    component: () => import('@/components/dashboard/CategoriePrincipaleDAchat.vue'),
                    props: (route) => ({
                        acheteurSiret: route.params.siret,
                        dateMin: route.query.dateMin,
                        dateMax: route.query.dateMax
                    })
                },
                {
                    path: 'acheteur/:siret/marches/top12',
                    component: () => import('@/components/dashboard/Top12.vue'),
                    props: (route) => ({
                        acheteurSiret: route.params.siret,
                        dateMin: route.query.dateMin,
                        dateMax: route.query.dateMax,
                        type: 'fournisseurs'
                    })
                },
                {
                    path: 'acheteur/:siret/marches/achat-durable',
                    component: () => import('@/components/dashboard/AchatDurable.vue'),
                    props: (route) => ({
                        acheteurSiret: route.params.siret,
                        dateMin: route.query.dateMin,
                        dateMax: route.query.dateMax
                    })
                },
                {
                    path: 'acheteur/:siret/concessions',
                    component: () => import('@/components/ListeConcessions.vue'),
                    props: (route) => ({
                        autoriteConcedanteSiret: route.params.siret,
                        dateMin: route.query.dateMin,
                        dateMax: route.query.dateMax
                    })
                }
            ]
        },
        {
            path: '/pages/notfound',
            name: 'notfound',
            component: () => import('@/views/pages/NotFound.vue')
        }
    ]
});

export default router;
