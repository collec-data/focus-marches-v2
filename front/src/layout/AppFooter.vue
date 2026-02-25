<script setup>
import { getOpsnRegion } from '@/service/HelpersService';
</script>

<template>
    <footer class="layout-footer card">
        <div>
            <h2 class="text-center">A propos de cet outil</h2>
            <div class="columns-2">
                <p>
                    Cet outil est alimenté avec les données du profil d'acheteur de la salle de marchés de {{ getOpsnRegion() }}. Certaines données peuvent manquer suite à des
                    <RouterLink to="/erreurs-importation"> <Button icon="pi pi-fw pi-exclamation-triangle" label="Erreurs d'importation" aria-label="Erreurs d'importation" variant="link"></Button> </RouterLink>
                </p>
                <p>
                    En savoir plus sur l'outil Focus Marchés sur notre page
                    <RouterLink to="/a-propos"> <Button icon="pi pi-fw pi-info-circle" label="A propos de Focus Marchés v2" aria-label="A propos de Focus Marchés v2" variant="link"></Button> </RouterLink>.
                </p>
                <p>
                    Notre page
                    <RouterLink to="/mentions-legales">
                        <Button icon="pi pi-fw pi-book" label="Mentions légales" aria-label="Mentions légales" variant="link"></Button>
                    </RouterLink>
                    contient des informations concernant la protection de la vie privée et vous permet de configurer le suivi ou pas par notre outil d'analyse de visites.
                </p>
            </div>
        </div>
    </footer>
</template>
