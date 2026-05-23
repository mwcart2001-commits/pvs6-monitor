<template>
  <div class="space-y-4">

    <!-- Loading / Error States -->
    <div v-if="loading" class="text-gray-500 text-sm">
      Loading panel data…
    </div>

    <div v-else-if="error" class="text-red-600 text-sm">
      Failed to load panel data
    </div>

    <div v-else>
      <!-- Row 1 -->
      <div class="flex flex-wrap justify-center gap-2">
        <PanelTile
          v-for="panel in row1Panels"
          :key="panel.physical_label"
          :label="panel.physical_label"
          :value="metric === 'power'
            ? (panel[metricMap[metric]] * 1000).toFixed(0)
            : panel[metricMap[metric]] ?? '—'"
          :unit="metric === 'power'
            ? 'W'
            : metric === 'voltage'
              ? 'V'
              : metric === 'current'
                ? 'A'
                : '°C'"
          :status="panel.status"
          class="w-20 sm:w-24"
        />
      </div>

      <!-- Row 2 -->
      <div class="flex flex-wrap justify-center gap-2">
        <PanelTile
          v-for="panel in row2Panels"
          :key="panel.physical_label"
          :label="panel.physical_label"
          :value="metric === 'power'
            ? (panel[metricMap[metric]] * 1000).toFixed(0)
            : panel[metricMap[metric]] ?? '—'"
          :unit="metric === 'power'
            ? 'W'
            : metric === 'voltage'
              ? 'V'
              : metric === 'current'
                ? 'A'
                : '°C'"
          :status="panel.status"
          class="w-20 sm:w-24"
        />
      </div>
    </div>

  </div>
</template>

<script setup>
import { computed, watch } from 'vue'
import PanelTile from './PanelTile.vue'
import { usePanels } from '../composables/usePanels'

/* Props */
const props = defineProps({
  metric: {
    type: String,
    required: true
  }
})

/* Load real panel data */
const { panels, loading, error } = usePanels()

const metricMap = {
  power: 'ac_power_kw',
  voltage: 'ac_voltage_v',
  current: 'ac_current_a',
  temperature: 'heatsink_temp_c'
}

/* Split into rows based on physical label */
const row1Panels = computed(() =>
  panels.value.filter(p => p.physical_label?.startsWith('R1'))
)

const row2Panels = computed(() =>
  panels.value.filter(p => p.physical_label?.startsWith('R2'))
)

watch(panels, () => {
  console.log("PANELS:", JSON.stringify(panels.value, null, 2))
})

</script>

<style scoped>
/* Optional: add spacing or responsive tweaks here */
</style>
