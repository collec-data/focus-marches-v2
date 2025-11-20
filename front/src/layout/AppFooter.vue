<script setup>
import { getOpsnRegion } from '@/service/HelpersService';
</script>

<template>
    <footer class="layout-footer card">
        <div>
            <h2 class="text-center">A propos de cet outil</h2>
            <div class="columns-2">
                <p>Cet outil est alimenté avec les données du profil d'acheteur de la salle de marchés de {{ getOpsnRegion() }}.</p>
                <p>Il a été conçu par le service Données Ouvertes de ARNia pour faciliter l'exploitation des informations contenues dans les données essentielles de la commande publique.</p>
                <p>Données publiées sous la Licence Ouverte Version 2.0 - Etalab. Le téléchargement des données se fait librement sur le portail opendata national.</p>
                <p>Notre page Mentions légales contient des informations concernant la protection de la vie privée et vous permet de configurer le suivi ou pas par notre outil d'analyse de visites.</p>
            </div>
        </div>
    </footer>
</template>
