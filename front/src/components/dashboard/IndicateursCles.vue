<script setup>
import { getIndicateursMarcheIndicateursGet } from '@/client';
import { onMounted, ref } from 'vue';

const props = defineProps({ acheteur_uid: { type: [String, null], default: null }, vendeur_uid: { type: [String, null], default: null } });

const indicateurs = ref({});

onMounted(() => {
    getIndicateursMarcheIndicateursGet({ query: { date_debut: '2010-01-01', acheteur_uid: props.acheteur_uid, vendeur_uid: props.vendeur_uid } }).then((data) => {
        indicateurs.value = data.data;
    });
});
</script>

<template>
    <section class="flex flex-col">
        <div>
            <h2 class="title">Indicateurs clés</h2>
            <p class="subtitle">
                Principaux indicateurs des <span class="highlight">{{ indicateurs.periode }} derniers mois</span>.
            </p>
        </div>
        <div class="flex flex-row flex-wrap gap-10 mt-10">
            <div class="indicateur">
                <i class="pi pi-calendar"></i>
                <div class="label">PÉRIODE</div>
                <div class="value">{{ indicateurs.periode }} mois</div>
            </div>
            <div class="indicateur">
                <i class="pi pi-receipt"></i>
                <div class="label">NB DE CONTRATS</div>
                <div class="value">{{ indicateurs.nb_contrats }}</div>
            </div>
            <div class="indicateur">
                <i class="pi pi-calculator"></i>
                <div class="label">MONTANT TOTAL</div>
                <div class="value">{{ Math.round(indicateurs.montant_total * 100) / 100 }} €</div>
            </div>
            <div v-if="acheteur_uid == null" class="indicateur">
                <i class="pi pi-users"></i>
                <div class="label">NB ACHETEURS</div>
                <div class="value">{{ indicateurs.nb_acheteurs }}</div>
            </div>
            <div v-if="vendeur_uid == null" class="indicateur">
                <i class="pi pi-users"></i>
                <div class="label">NB FOURNISSEURS</div>
                <div class="value">{{ indicateurs.nb_fournisseurs }}</div>
            </div>
            <div class="indicateur">
                <i class="pi pi-sitemap"></i>
                <div class="label">NB CONTRATS AVEC SOUS TRAITANCE</div>
                <div class="value">{{ indicateurs.nb_sous_traitance }}</div>
            </div>
            <div class="indicateur">
                <i class="pi pi-star"></i>
                <div class="label">NB CONTRATS AVEC DES CONSIDERATIONS ENVIRONNEMENTALES ET SOCIALES</div>
                <div class="value"></div>
            </div>
            <div class="indicateur">
                <i class="pi pi-globe"></i>
                <div class="label">NB CONTRATS AVEC DES CONSIDERATIONS ENVIRONNEMENTALES</div>
                <div class="value"></div>
            </div>
            <div class="indicateur">
                <i class="pi pi-eye"></i>
                <div class="label">NB CONTRATS AVEC DES CONSIDERATIONS SOCIALES</div>
                <div class="value"></div>
            </div>
            <div class="indicateur">
                <i class="pi pi-lightbulb"></i>
                <div class="label">NB CONTRATS INNOVANTS</div>
                <div class="value">{{ indicateurs.nb_innovant }}</div>
            </div>
        </div>
    </section>
</template>

<style scoped>
.indicateur {
    flex-basis: 15rem;
    flex-shrink: 0;
    text-align: center;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.value {
    font-weight: 900;
}

.pi {
    color: var(--p-primary-color);
    font-size: 4rem;
}
</style>
