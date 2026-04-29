<template>
  <div class="p-6 space-y-10">

    <!-- Page Title -->
    <h1 class="text-3xl font-semibold tracking-tight">Current System Status</h1>

    <!-- System Overview Section -->
    <section class="bg-white rounded-xl shadow p-6 space-y-6">
      <h2 class="text-xl font-medium text-gray-700">System Overview</h2>

      <!-- Summary Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <SystemSummaryCard
          label="Solar Generation"
          :value="solar.toFixed(2)"
          unit="kW"
        />
        <SystemSummaryCard
          label="Home Load"
          :value="load.toFixed(2)"
          unit="kW"
        />
        <SystemSummaryCard
          label="Net Power"
          :value="net.toFixed(2)"
          unit="kW"
        />
        <SystemSummaryCard
          label="Grid Import/Export"
          :value="grid.toFixed(2)"
          unit="kW"
        />
      </div>
    </section>

    <!-- Panel Metric Selector -->
    <section class="space-y-4">
      <h2 class="text-xl font-medium text-gray-700">Panel Metrics</h2>

      <div class="flex flex-wrap gap-3">
        <button
          v-for="metric in metrics"
          :key="metric.key"
          @click="selectedMetric = metric.key"
          :class="[
            'px-4 py-2 rounded-lg transition',
            selectedMetric === metric.key
              ? 'bg-blue-600 text-white shadow'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          ]"
        >
          {{ metric.label }}
        </button>
      </div>
    </section>

    <!-- Panel Layout -->
    <section class="space-y-4">
      <h2 class="text-xl font-medium text-gray-700">Panel Layout</h2>
      <PanelGrid :metric="selectedMetric" />
    </section>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import SystemSummaryCard from '../components/SystemSummaryCard.vue'
import PanelGrid from '../components/PanelGrid.vue'

/* -----------------------------
   System Snapshot State
------------------------------ */
const loading = ref(true)
const error = ref(null)

const solar = ref(0)
const load = ref(0)
const net = ref(0)
const grid = ref(0)

/* -----------------------------
   Panel Metric Selector
------------------------------ */
const selectedMetric = ref('ac_power')

const metrics = [
  { key: 'ac_power_kw', label: 'AC Power' },
  { key: 'dc_power_kw', label: 'DC Power' },
  { key: 'ac_voltage_v', label: 'Voltage' },
  { key: 'heatsink_temp_c', label: 'Temperature' },
  { key: 'health_score', label: 'Health Score' }
]

/* -----------------------------
   Fetch System Snapshot
------------------------------ */
onMounted(async () => {
  try {
    const res = await fetch('/api/system/current')
    if (!res.ok) throw new Error('Failed to fetch system snapshot')

    const data = await res.json()

    solar.value = data.solar_kw ?? 0
    load.value = data.load_kw ?? 0
    net.value = data.net_kw ?? 0
    grid.value = data.grid_kw ?? 0
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
})
</script>
