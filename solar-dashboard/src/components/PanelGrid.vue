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
      <div class="flex gap-2">
        <PanelTile
          v-for="panel in row1Panels"
          :key="panel.physical_label"
          :label="panel.physical_label"
          :value="panel[metric] ?? '—'"
          :status="panel.status"
        />
      </div>

      <!-- Row 2 -->
      <div class="flex gap-2">
        <PanelTile
          v-for="panel in row2Panels"
          :key="panel.physical_label"
          :label="panel.physical_label"
          :value="panel[metric] ?? '—'"
          :status="panel.status"
        />
      </div>
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
const { panels, loading, error } = usePanels()

/* Split into rows based on physical label */
const row1Panels = computed(() =>
  panels.value.filter(p => p.physical_label?.startsWith('R1'))
)

const row2Panels = computed(() =>
  panels.value.filter(p => p.physical_label?.startsWith('R2'))
)
</script>

<style scoped>
/* Optional: add spacing or responsive tweaks here */
</style>
