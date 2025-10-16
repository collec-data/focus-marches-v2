import AppLayout from '@/layout/AppLayout.vue';
import WidgetLayout from '@/layout/WidgetLayout.vue';
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
                }
            ]
        },
        {
            path: '/widget/',
            component: WidgetLayout,
            props: { boutonWidget: false },
            children: [
                {
                    path: 'acheteur/:uid',
                    component: () => import('@/components/DetailsAcheteur.vue'),
                    props: (route) => ({
                        acheteurUid: route.params.uid
                    })
                },
                {
                    path: 'indicateurs',
                    component: () => import('@/components/dashboard/IndicateursCles.vue'),
                    props: (route) => ({
                        acheteurUid: route.query.acheteurUid,
                        vendeurUid: route.query.vendeurUid,
                        dateMin: route.query.dateMin,
                        dateMax: route.query.dateMax
                    })
                },
                {
                    path: 'marches',
                    component: () => import('@/components/ListeMarches.vue'),
                    props: (route) => ({
                        acheteurUid: route.query.acheteurUid,
                        vendeurUid: route.query.vendeurUid,
                        dateMin: route.query.dateMin,
                        dateMax: route.query.dateMax
                    })
                },
                {
                    path: 'distribution-marches',
                    component: () => import('@/components/dashboard/DistributionTemporelleMarches.vue'),
                    props: (route) => ({
                        acheteurUid: route.query.acheteurUid,
                        vendeurUid: route.query.vendeurUid,
                        dateMin: route.query.dateMin,
                        dateMax: route.query.dateMax
                    })
                },
                {
                    path: 'nature-marches',
                    component: () => import('@/components/dashboard/NatureContrats.vue'),
                    props: (route) => ({
                        acheteurUid: route.query.acheteurUid,
                        vendeurUid: route.query.vendeurUid,
                        dateMin: route.query.dateMin,
                        dateMax: route.query.dateMax
                    })
                },
                {
                    path: 'procedure-marches',
                    component: () => import('@/components/dashboard/Procedure.vue'),
                    props: (route) => ({
                        acheteurUid: route.query.acheteurUid,
                        vendeurUid: route.query.vendeurUid,
                        dateMin: route.query.dateMin,
                        dateMax: route.query.dateMax
                    })
                },
                {
                    path: 'ccag-marches',
                    component: () => import('@/components/dashboard/CCAG.vue'),
                    props: (route) => ({
                        acheteurUid: route.query.acheteurUid,
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
