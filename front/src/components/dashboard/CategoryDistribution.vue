<template>
  <section class="category-distribution">
    <h2 class="title">Distribution par catégorie principale d'achat</h2>
    <p class="subtitle">
      Comparaison des trois catégories d'achats (zone colorée) par rapport au total (zone grise).
    </p>
    <div class="charts-row">
      <div v-for="cat in categories" :key="cat.key" class="chart-block">
        <h3 class="chart-title">{{ cat.label }}</h3>
        <Chart
          type="line"
          :data="cat.chartData"
          :options="chartOptions(cat.color)"
          class="category-chart"
        />
        <div class="stats-row">
          <div class="stats-box">
            <div class="stats-label">Nombre :</div>
            <span class="stats-value" :style="{background:cat.color}">{{ cat.nb }} marchés</span>
            <span class="stats-total">{{ cat.nbTotal }} marchés</span>
          </div>
          <div class="stats-box">
            <div class="stats-label">Montant :</div>
            <span class="stats-value" :style="{background:cat.color}">{{ cat.amount }} €</span>
            <span class="stats-total">{{ cat.amountTotal }} €</span>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import Chart from 'primevue/chart';
import { ref } from 'vue';

const categories = ref([
  {
    key: 'services',
    label: 'SERVICES',
    color: '#3cb371',
    nb: 96,
    nbTotal: 200,
    amount: '42 158 965',
    amountTotal: '58 584 431',
    chartData: {
      labels: ['2022', '2023', '2024', '2025'],
      datasets: [
        {
          label: 'Services',
          data: [2, 5, 16, 0],
          fill: true,
          backgroundColor: 'rgba(60,179,113,0.2)',
          borderColor: '#3cb371',
          tension: 0.4,
        },
        {
          label: 'Total',
          data: [3, 7, 21, 0],
          fill: true,
          backgroundColor: 'rgba(180,180,180,0.2)',
          borderColor: '#bbb',
          tension: 0.4,
        },
      ],
    },
  },
  {
    key: 'travaux',
    label: 'TRAVAUX',
    color: '#6fa8dc',
    nb: 76,
    nbTotal: 200,
    amount: '14 636 200',
    amountTotal: '58 584 431',
    chartData: {
      labels: ['2022', '2023', '2024', '2025'],
      datasets: [
        {
          label: 'Travaux',
          data: [1, 4, 5, 0],
          fill: true,
          backgroundColor: 'rgba(111,168,220,0.2)',
          borderColor: '#6fa8dc',
          tension: 0.4,
        },
        {
          label: 'Total',
          data: [3, 7, 21, 0],
          fill: true,
          backgroundColor: 'rgba(180,180,180,0.2)',
          borderColor: '#bbb',
          tension: 0.4,
        },
      ],
    },
  },
  {
    key: 'fournitures',
    label: 'FOURNITURES',
    color: '#f6b26b',
    nb: 28,
    nbTotal: 200,
    amount: '1 789 266',
    amountTotal: '58 584 431',
    chartData: {
      labels: ['2022', '2023', '2024', '2025'],
      datasets: [
        {
          label: 'Fournitures',
          data: [0, 1, 1, 0],
          fill: true,
          backgroundColor: 'rgba(246,178,107,0.2)',
          borderColor: '#f6b26b',
          tension: 0.4,
        },
        {
          label: 'Total',
          data: [3, 7, 21, 0],
          fill: true,
          backgroundColor: 'rgba(180,180,180,0.2)',
          borderColor: '#bbb',
          tension: 0.4,
        },
      ],
    },
  },
]);

function chartOptions(color) {
  return {
    plugins: {
      legend: { display: false },
      tooltip: { enabled: true },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(value) {
            if (value >= 1000000) return value/1000000 + 'M';
            if (value >= 1000) return value/1000 + 'k';
            return value;
          }
        }
      }
    },
    elements: {
      line: { borderWidth: 2 },
      point: { radius: 0 }
    },
    maintainAspectRatio: false,
    responsive: true,
    backgroundColor: color
  };
}
</script>

<style scoped>
.category-distribution {
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
.charts-row {
  display: flex;
  flex-wrap: wrap;
  gap: 2rem 1.5rem;
  justify-content: space-between;
}
.chart-block {
  flex: 1 1 300px;
  min-width: 260px;
  max-width: 350px;
  background: #f8fbfd;
  border-radius: 10px;
  padding: 1.2rem 1rem 1.5rem 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 1px 4px rgba(126,214,247,0.07);
}
.chart-title {
  color: #888;
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  letter-spacing: 1px;
  text-align: center;
}
.category-chart {
  width: 100%;
  height: 180px;
  margin-bottom: 1.2rem;
}
.stats-row {
  display: flex;
  gap: 1.2rem;
  width: 100%;
  justify-content: center;
}
.stats-box {
  background: #f4f4f4;
  border-radius: 6px;
  padding: 0.5rem 0.7rem;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  min-width: 110px;
}
.stats-label {
  color: #888;
  font-size: 0.95rem;
  margin-bottom: 0.2rem;
}
.stats-value {
  color: #fff;
  font-weight: 700;
  border-radius: 4px;
  padding: 0.1rem 0.5rem;
  margin-bottom: 0.2rem;
  display: inline-block;
  font-size: 1.05rem;
}
.stats-total {
  color: #888;
  font-size: 0.95rem;
  margin-left: 0.2rem;
}
@media (max-width: 900px) {
  .charts-row {
    gap: 1.5rem 0.5rem;
  }
  .chart-block {
    min-width: 180px;
    max-width: 250px;
    padding: 1rem 0.5rem 1.2rem 0.5rem;
  }
}
@media (max-width: 600px) {
  .charts-row {
    flex-direction: column;
    gap: 1.2rem;
    align-items: center;
  }
  .chart-block {
    width: 100%;
    max-width: 350px;
  }
}
</style>
