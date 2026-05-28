<template>
  <div class="p-6 space-y-10">

    <!-- Page Title -->
    <h1 class="text-3xl font-semibold tracking-tight">Current System Status</h1>

    <!-- Energy Summary Card -->
    <section class="bg-white rounded-xl shadow p-6 space-y-6">
      <SystemEnergySummary />
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
import SystemEnergySummary from '../components/SystemEnergySummary.vue'
import PanelGrid from '../components/PanelGrid.vue'
import { useSystemSnapshot } from '../composables/useSystemSnapshot'

const { system, loadSystem } = useSystemSnapshot()

const metrics = [
  { key: 'power', label: 'Power (W)' },
  { key: 'voltage', label: 'Voltage (V)' },
  { key: 'current', label: 'Current (A)' },
  { key: 'temperature', label: 'Temperature (°F)' }
]

const selectedMetric = ref('power')

onMounted(() => {
  loadSystem()
})
</script>
