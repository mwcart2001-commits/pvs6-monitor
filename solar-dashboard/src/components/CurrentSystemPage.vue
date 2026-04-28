<template>
  <div class="p-6 space-y-8">

    <h1 class="text-2xl font-bold">Current System Status</h1>

    <!-- Loading -->
    <p v-if="loading">Loading system snapshot…</p>

    <!-- Error -->
    <p v-else-if="error" class="text-red-600">
      Failed to load system snapshot: {{ error }}
    </p>

    <!-- Summary Cards -->
    <div v-else class="flex gap-4 flex-wrap">
      <SystemSummaryCard
        label="Solar Generation"
        :value="snapshot.solar_kw"
        unit="kW"
      />
      <SystemSummaryCard
        label="Home Load"
        :value="snapshot.load_kw"
        unit="kW"
      />
      <SystemSummaryCard
        label="Net Power"
        :value="snapshot.net_kw"
        unit="kW"
      />
      <SystemSummaryCard
        label="Grid Import/Export"
        :value="snapshot.grid_kw"
        unit="kW"
      />
    </div>

    <!-- Panel Grid -->
    <PanelGrid />

  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useSystemSnapshot } from '../composables/useSystemSnapshot'

import SystemSummaryCard from '../components/SystemSummaryCard.vue'
import PanelGrid from '../components/PanelGrid.vue'

const { data, loading, error } = useSystemSnapshot()

const snapshot = computed(() => data.value || {})
</script>
