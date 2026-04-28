<template>
  <div class="space-y-4">

    <!-- Row 1 -->
    <div class="flex gap-2">
      <PanelTile
        v-for="panel in row1Panels"
        :key="panel.physical_label"
        :label="panel.physical_label"
        :value="panel[metric]"
      />
    </div>

    <!-- Row 2 -->
    <div class="flex gap-2">
      <PanelTile
        v-for="panel in row2Panels"
        :key="panel.physical_label"
        :label="panel.physical_label"
        :value="panel[metric]"
      />
    </div>

  </div>
</template>

<script setup>
import { computed } from 'vue'
import PanelTile from './PanelTile.vue'

/* Props */
const props = defineProps({
  metric: {
    type: String,
    required: true
  }
})

/* Example panel data structure:
   You will replace this with real API data soon.
*/
const panels = [
  { physical_label: 'R1C1', ac_power: 120, dc_power: 130, voltage: 38, temperature: 45, health: 98 },
  { physical_label: 'R1C2', ac_power: 118, dc_power: 129, voltage: 37, temperature: 44, health: 97 },
  // ...
  // All 15 panels
]

/* Split into rows based on physical label */
const row1Panels = computed(() =>
  panels.filter(p => p.physical_label.startsWith('R1'))
)

const row2Panels = computed(() =>
  panels.filter(p => p.physical_label.startsWith('R2'))
)
</script>
