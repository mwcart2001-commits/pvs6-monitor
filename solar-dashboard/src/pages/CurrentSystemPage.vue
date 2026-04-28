<template>
  <div class="p-6 space-y-8">

    <h1 class="text-2xl font-bold">Current System Status</h1>

    <!-- Loading State -->
    <div v-if="loading" class="text-gray-500">
      Loading system data…
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="text-red-600">
      {{ error }}
    </div>

    <!-- System Summary Cards -->
    <div v-else class="flex gap-4 flex-wrap">
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

    <!-- Panel Grid -->
    <PanelGrid />

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import SystemSummaryCard from '../components/SystemSummaryCard.vue'
import PanelGrid from '../components/PanelGrid.vue'

const loading = ref(true)
const error = ref(null)

const solar = ref(0)
const load = ref(0)
const net = ref(0)
const grid = ref(0)

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

