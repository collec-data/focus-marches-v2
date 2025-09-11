<template>
  <section class="buyers-ranking">
    <h2 class="title">Qui achète ?</h2>
    <p class="subtitle">
      Top 12 des acheteurs classés par montant total des contrats conclus au cours de <span class="highlight">71 derniers mois</span>.
      Survolez les noms les acheteurs pour les afficher en entier.
    </p>
    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        :class="['tab', {active: tab.key === selectedTab}]"
        @click="selectedTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>
    <div class="buyers-chart-row">
      <div class="buyers-list">
        <div
          v-for="(buyer, i) in sortedBuyersData[selectedTab]"
          :key="buyer.name"
          class="buyer-item"
        >
          <span class="buyer-name" :title="buyer.name">{{ buyer.name }}</span>
          <span class="buyer-amount">{{ buyer.amount }} €</span>
        </div>
      </div>
      <div class="buyers-bar-chart">
        <Chart
          type="bar"
          :data="barChartData"
          :options="barChartOptions"
          class="buyers-chart"
        />
      </div>
    </div>
    <a href="#" class="buyers-link">
      <i class="pi pi-list"></i> Liste complète des organismes acheteurs
    </a>
  </section>
</template>

<script setup>
import { ref, computed } from 'vue';
import Chart from 'primevue/chart';

const tabs = [
  { key: 'all', label: 'Tous les marchés' },
  { key: 'services', label: 'Services' },
  { key: 'travaux', label: 'Travaux' },
  { key: 'fournitures', label: 'Fournitures' },
];
const selectedTab = ref('all');

// Données factices, à remplacer par des props ou une API
const buyersData = {
  all: [
    { name: "Groupement d'Intérêt Public Recia", amount: '182 144 780' },
    { name: 'Commune', amount: '26 337 311' },
    { name: 'Commune de Montargis -', amount: '15 767 728' },
    { name: ",Commune d’Amboise", amount: '12 491 123' },
    { name: 'Communauté de Communes ...', amount: '9 689 556' },
    { name: 'Communauté de Communes ...', amount: '9 059 750' },
    { name: 'Commune de Montlouis-sur-Loire', amount: '7 683 038' },
    { name: 'Commune de Saint Doulcha ...', amount: '5 707 104' },
    { name: 'Communauté de Communes ...', amount: '5 663 330' },
    { name: ",Commune d’Issoudun", amount: '5 068 221' },
    { name: 'GIP Alfa Centre', amount: '4 963 038' },
    { name: 'Commune de Mehun-sur-Yè ...', amount: '4 841 867' },
  ],
  services: [
    { name: "Groupement d'Intérêt Public Recia", amount: '120 000 000' },
    { name: 'Commune', amount: '10 000 000' },
    // ...
  ],
  travaux: [
    { name: 'Commune de Montargis -', amount: '8 000 000' },
    // ...
  ],
  fournitures: [
    { name: 'GIP Alfa Centre', amount: '2 000 000' },
    // ...
  ],
};

// Fonction utilitaire pour trier par montant décroissant
function sortBuyersByAmount(arr) {
  return arr.slice().sort((a, b) => {
    const aVal = parseInt(a.amount.replace(/\s/g, ''));
    const bVal = parseInt(b.amount.replace(/\s/g, ''));
    return bVal - aVal;
  });
}

const sortedBuyersData = {};
for (const key in buyersData) {
  sortedBuyersData[key] = sortBuyersByAmount(buyersData[key]);
}

const barColors = [
  '#f6d7a7', '#f6b26b', '#b6d7a8', '#a2c4c9', '#b4a7d6', '#a4c2f4', '#b7b7b7', '#ffd966', '#d9ead3', '#cfe2f3', '#f4cccc', '#ead1dc'
];

const barChartData = computed(() => {
  const buyers = sortedBuyersData[selectedTab.value];
  return {
    labels: buyers.map(b => b.name),
    datasets: [
      {
        label: 'Montant',
        data: buyers.map(b => parseInt(b.amount.replace(/\s/g, ''))),
        backgroundColor: barColors,
        borderRadius: 6,
        maxBarThickness: 40,
      },
    ],
  };
});

const barChartOptions = {
  indexAxis: 'y',
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        label: ctx => ctx.parsed.x.toLocaleString('fr-FR') + ' €',
      },
    },
  },
  scales: {
    x: {
      beginAtZero: true,
      ticks: {
        callback: value => {
          if (value >= 1000000) return value / 1000000 + 'M';
          if (value >= 1000) return value / 1000 + 'k';
          return value;
        },
      },
      grid: { color: '#eee' },
    },
    y: {
      ticks: {
        callback: value => value.length > 18 ? value.slice(0, 18) + '…' : value,
        color: '#888',
      },
      grid: { display: false },
    },
  },
  responsive: true,
  maintainAspectRatio: false,
  layout: { padding: { left: 0, right: 0, top: 0, bottom: 0 } },
};
</script>

<style scoped>
.buyers-ranking {
  background: #fff;
  border-radius: 12px;
  padding: 2rem 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  max-width: 1200px;
  margin: 2rem auto;
}
.title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: #222;
}
.subtitle {
  color: #888;
  margin-bottom: 2.5rem;
  font-size: 1.1rem;
}
.highlight {
  color: #222;
  font-weight: 600;
}
.tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}
.tab {
  background: #f4f4f4;
  border: 1px solid #ccc;
  border-bottom: none;
  border-radius: 4px 4px 0 0;
  padding: 0.5rem 1.2rem;
  font-weight: 600;
  color: #888;
  cursor: pointer;
  transition: background 0.2s;
}
.tab.active {
  background: #fff;
  color: #222;
  border-bottom: 2px solid #f6b26b;
}
.buyers-chart-row {
  display: flex;
  gap: 2rem;
  align-items: flex-start;
}
.buyers-list {
  flex: 0 0 270px;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.buyer-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #f4f4f4;
  border-radius: 6px;
  padding: 0.3rem 0.7rem;
  font-size: 1rem;
  margin-bottom: 0.1rem;
}
.buyer-name {
  color: #444;
  font-weight: 500;
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  cursor: pointer;
}
.buyer-amount {
  background: #eaeaea;
  border-radius: 4px;
  color: #888;
  font-weight: 600;
  padding: 0.1rem 0.5rem;
  margin-left: 0.5rem;
  font-size: 0.98rem;
}
.buyers-bar-chart {
  flex: 1 1 0;
  min-width: 0;
  height: 400px;
  display: flex;
  align-items: center;
}
.buyers-chart {
  width: 100%;
  height: 100%;
}
.buyers-link {
  display: inline-block;
  margin-top: 1.5rem;
  color: #2980b9;
  font-weight: 500;
  text-decoration: none;
  font-size: 1.05rem;
  transition: color 0.2s;
}
.buyers-link:hover {
  color: #1a5276;
  text-decoration: underline;
}
@media (max-width: 900px) {
  .buyers-chart-row {
    flex-direction: column;
    gap: 1.2rem;
  }
  .buyers-list {
    flex: 1 1 100%;
    max-width: 100%;
    margin-bottom: 1rem;
  }
  .buyers-bar-chart {
    height: 300px;
  }
}
@media (max-width: 600px) {
  .buyers-bar-chart {
    height: 220px;
  }
}
</style>
