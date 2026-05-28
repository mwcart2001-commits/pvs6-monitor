<template>
  <div class="space-y-4">

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
          :value="formatValue(panel)"
          :unit="unitForMetric"
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
          :value="formatValue(panel)"
          :unit="unitForMetric"
          :status="panel.status"
          class="w-20 sm:w-24"
        />
      </div>
    </div>

  </div>
</template>

<script setup>
import { computed } from 'vue'
import PanelTile from './PanelTile.vue'
import { usePanels } from '../composables/usePanels'

const props = defineProps({
  metric: {
    type: String,
    required: true
  }
})

const { panels, loading, error } = usePanels()

const metricMap = {
  power: 'ac_power_kw',
  voltage: 'ac_voltage_v',
  current: 'ac_current_a',
  temperature: 'heatsink_temp_c'
}

const unitForMetric = computed(() => {
  if (props.metric === 'power') return 'W'
  if (props.metric === 'voltage') return 'V'
  if (props.metric === 'current') return 'A'
  if (props.metric === 'temperature') return '°F'
  return ''
})

function formatValue(panel) {
  const raw = panel[metricMap[props.metric]]

  if (raw == null) return '—'

  if (props.metric === 'power') {
    return (raw * 1000).toFixed(0)
  }

  if (props.metric === 'temperature') {
    return ((raw * 9/5) + 32).toFixed(1)
  }

  return raw
}

const row1Panels = computed(() =>
  panels.value.filter(p => p.physical_label?.startsWith('R1'))
)

const row2Panels = computed(() =>
  panels.value.filter(p => p.physical_label?.startsWith('R2'))
)
</script>
