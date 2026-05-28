<template>
  <div class="summary-card">
    <div class="tabs">
      <button
        v-for="t in tabs"
        :key="t.key"
        :disabled="t.key === activeTab"
        :class="{ active: t.key === activeTab }"
        @click="setTab(t.key)"
      >
        {{ t.label }}
      </button>
    </div>

    <div v-if="loading" class="loading">Loading summary…</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <div v-else class="summary-grid">
      <div class="item">
        <label>Production</label>
        <span>{{ summary.production_kwh }} kWh</span>
      </div>
      <div class="item">
        <label>Consumption</label>
        <span>{{ summary.consumption_kwh }} kWh</span>
      </div>
      <div class="item">
        <label>Grid Import</label>
        <span>{{ summary.grid_import_kwh }} kWh</span>
      </div>
      <div class="item">
        <label>Grid Export</label>
        <span>{{ summary.grid_export_kwh }} kWh</span>
      </div>
      <div class="item">
        <label>Net</label>
        <span>{{ summary.net_kwh }} kWh</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";

const tabs = [
  { key: "day", label: "Today" },
  { key: "week", label: "This Week" },
  { key: "month", label: "This Month" },
  { key: "year", label: "This Year" },
];

const activeTab = ref("day");

const summary = ref({
  production_kwh: 0,
  consumption_kwh: 0,
  grid_import_kwh: 0,
  grid_export_kwh: 0,
  net_kwh: 0
});

const loading = ref(false);
const error = ref("");

const endpoints = {
  day: () => `/api/summary/daily?date=${new Date().toISOString().slice(0, 10)}`,
  week: () => `/api/summary/weekly?date=${new Date().toISOString().slice(0, 10)}`,
  month: () => `/api/summary/monthly?date=${new Date().toISOString().slice(0, 10)}`,
  year: () => `/api/summary/yearly?date=${new Date().getFullYear()}`
};

function setTab(tab) {
  activeTab.value = tab;
}

async function loadSummary() {
  loading.value = true;
  error.value = "";

  try {
    const url = endpoints[activeTab.value]();
    const res = await fetch(url);
    const data = await res.json();

    if (data.error) {
      error.value = data.error;
    } else {
      summary.value = data;
    }
  } catch {
    error.value = "Failed to load summary";
  }

  loading.value = false;
}

watch(activeTab, loadSummary);

// initial load
loadSummary();
</script>

<style scoped>
.summary-card {
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.tabs button {
  padding: 6px 12px;
  border: none;
  background: #eee;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.tabs button.active {
  background: #007bff;
  color: white;
}

.tabs button:disabled {
  opacity: 0.7;
  cursor: default;
}

.loading,
.error {
  padding: 12px;
  font-size: 14px;
  color: #666;
}

.error {
  color: #b00020;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  animation: fadeIn .25s ease-out;
}

.item label {
  font-size: 12px;
  color: #666;
}

.item span {
  font-size: 18px;
  font-weight: bold;
}

@keyframes fadeIn {
  from { opacity: 0 }
  to { opacity: 1 }
}
</style>
