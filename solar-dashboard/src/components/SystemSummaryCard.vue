<template>
  <div class="summary-card">
    <div class="tabs">
      <button
        v-for="t in tabs"
        :key="t.key"
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
import { ref } from "vue";

const tabs = [
  { key: "day", label: "Today" },
  { key: "week", label: "This Week" },
  { key: "month", label: "This Month" },
  { key: "year", label: "This Year" },
];

const activeTab = ref("day");
const summary = ref({});
const loading = ref(false);
const error = ref("");

function setTab(tab) {
  activeTab.value = tab;
  loadSummary();
}

async function loadSummary() {
  loading.value = true;
  error.value = "";

  try {
    const now = new Date();
    let url = "";

    if (activeTab.value === "day") {
      const date = now.toISOString().slice(0, 10);
      url = `/api/summary/daily?date=${date}`;
    }

    if (activeTab.value === "week") {
      const date = now.toISOString().slice(0, 10);
      url = `/api/summary/weekly?date=${date}`;
    }

    if (activeTab.value === "month") {
      const date = now.toISOString().slice(0, 10);
      url = `/api/summary/monthly?date=${date}`;
    }

    if (activeTab.value === "year") {
      const year = now.getFullYear();
      url = `/api/summary/yearly?date=${year}`;
    }

    const res = await fetch(url);
    const data = await res.json();

    if (data.error) {
      error.value = data.error;
    } else {
      summary.value = data;
    }
  } catch (e) {
    error.value = "Failed to load summary";
  }

  loading.value = false;
}

// Load initial tab
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
}

.item label {
  font-size: 12px;
  color: #666;
}

.item span {
  font-size: 18px;
  font-weight: bold;
}
</style>
