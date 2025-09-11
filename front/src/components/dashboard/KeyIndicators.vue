<template>
  <section class="key-indicators">
    <h2 class="title">Indicateurs clés</h2>
    <p class="subtitle">
      Principaux indicateurs des <span class="highlight">71 derniers mois</span>.
    </p>
    <div class="indicators-grid">
      <div class="indicator">
        <div class="icon">
          <!-- Calendar SVG -->
          <svg width="40" height="40" fill="#7ed6f7" viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 9h18" stroke="#7ed6f7" stroke-width="2" fill="none"/></svg>
        </div>
        <div class="label">PÉRIODE</div>
        <div class="value">71 mois</div>
      </div>
      <div class="indicator">
        <div class="icon">
          <!-- Handshake SVG -->
          <svg width="40" height="40" fill="#7ed6f7" viewBox="0 0 24 24"><path d="M17 13l4-4a2 2 0 0 0-2.8-2.8l-4 4" stroke="#7ed6f7" stroke-width="2" fill="none"/><path d="M7 11l-4-4a2 2 0 0 1 2.8-2.8l4 4" stroke="#7ed6f7" stroke-width="2" fill="none"/><path d="M8 12l4 4 4-4" stroke="#7ed6f7" stroke-width="2" fill="none"/></svg>
        </div>
        <div class="label">NB DE CONTRATS</div>
        <div class="value">935</div>
      </div>
      <div class="indicator">
        <div class="icon">
          <!-- Calculator SVG -->
          <svg width="40" height="40" fill="#7ed6f7" viewBox="0 0 24 24"><rect x="5" y="3" width="14" height="18" rx="2"/><rect x="8" y="7" width="8" height="2" rx="1" fill="#fff"/><circle cx="9" cy="15" r="1.5" fill="#fff"/><circle cx="12" cy="15" r="1.5" fill="#fff"/><circle cx="15" cy="15" r="1.5" fill="#fff"/></svg>
        </div>
        <div class="label">MONTANT TOTAL</div>
        <div class="value">318 917 428 €</div>
      </div>
      <div class="indicator">
        <div class="icon">
          <!-- Users SVG -->
          <svg width="40" height="40" fill="#7ed6f7" viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M2 20c0-4 8-6 10-6s10 2 10 6" stroke="#7ed6f7" stroke-width="2" fill="none"/></svg>
        </div>
        <div class="label">NB ACHETEURS</div>
        <div class="value">52</div>
      </div>
      <div class="indicator">
        <div class="icon">
          <!-- Users SVG -->
          <svg width="40" height="40" fill="#7ed6f7" viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M2 20c0-4 8-6 10-6s10 2 10 6" stroke="#7ed6f7" stroke-width="2" fill="none"/></svg>
        </div>
        <div class="label">NB FOURNISSEURS</div>
        <div class="value">1500</div>
      </div>
    </div>
  </section>
</template>

<script setup>
// Pas de logique dynamique pour l'instant
</script>

<style scoped>
.key-indicators {
  background: #fff;
  border-radius: 12px;
  padding: 2rem 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  max-width: 1100px;
  margin: 2rem auto;
}
.title {
  font-size: 1.7rem;
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
.indicators-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 2.5rem 1.5rem;
  justify-content: space-between;
}
.indicator {
  flex: 1 1 160px;
  min-width: 160px;
  max-width: 200px;
  background: #f8fbfd;
  border-radius: 10px;
  padding: 1.2rem 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 1px 4px rgba(126,214,247,0.07);
}
.icon {
  margin-bottom: 0.7rem;
}
.label {
  color: #7ed6f7;
  font-size: 0.95rem;
  font-weight: 600;
  margin-bottom: 0.3rem;
  letter-spacing: 1px;
  text-align: center;
}
.value {
  color: #444;
  font-size: 1.4rem;
  font-weight: 700;
  text-align: center;
}
@media (max-width: 900px) {
  .indicators-grid {
    gap: 1.5rem 0.5rem;
  }
  .indicator {
    min-width: 120px;
    max-width: 160px;
    padding: 1rem 0.5rem;
  }
}
@media (max-width: 600px) {
  .indicators-grid {
    flex-direction: column;
    gap: 1.2rem;
    align-items: center;
  }
  .indicator {
    width: 100%;
    max-width: 350px;
  }
}
</style>
