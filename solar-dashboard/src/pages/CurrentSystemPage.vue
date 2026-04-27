<template>
  <div class="p-6 space-y-8">

    <h1 class="text-2xl font-bold">Current System Status</h1>

    <!-- System Summary Cards -->
    <div class="flex gap-4 flex-wrap">
      <SystemSummaryCard label="Solar Generation" value="0.00" unit="kW" />
      <SystemSummaryCard label="Home Load" value="0.00" unit="kW" />
      <SystemSummaryCard label="Net Power" value="0.00" unit="kW" />
      <SystemSummaryCard label="Grid Import/Export" value="0.00" unit="kW" />
    </div>

    <!-- Panel Grid -->
    <PanelGrid />

  </div>
</template>

<script setup>
import SystemSummaryCard from '../components/SystemSummaryCard.vue'
import PanelGrid from '../components/PanelGrid.vue'
</script>

