import AppLayout from '@/layout/AppLayout.vue';
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
                    path: '/pages/empty',
                    name: 'empty',
                    component: () => import('@/views/pages/Empty.vue')
                },
                {
                    path: '/documentation',
                    name: 'documentation',
                    component: () => import('@/views/pages/Documentation.vue')
                }
            ]
        },
        {
            path: '/landing',
            name: 'landing',
            component: () => import('@/views/pages/Landing.vue')
        },
        {
            path: '/pages/notfound',
            name: 'notfound',
            component: () => import('@/views/pages/NotFound.vue')
        }
    ]
});

export default router;
