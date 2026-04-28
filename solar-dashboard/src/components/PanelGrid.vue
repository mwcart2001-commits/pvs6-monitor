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
import { usePanels } from '../composables/usePanels'

/* Props */
const props = defineProps({
  metric: {
    type: String,
    required: true
  }
})

/* Load real panel data */
const { panels } = usePanels()

/* Split into rows based on physical label */
const row1Panels = computed(() =>
  panels.value.filter(p => p.physical_label.startsWith('R1'))
)

const row2Panels = computed(() =>
  panels.value.filter(p => p.physical_label.startsWith('R2'))
)
</script>
