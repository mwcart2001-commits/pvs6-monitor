<template>
  <div
    class="p-3 rounded-md text-center text-sm font-medium w-20"
    :class="statusClass"
  >
    <div class="text-xs text-gray-700">{{ label }}</div>

    <div class="text-lg font-semibold mt-1">
      {{ displayValue }}
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

/* Props */
const props = defineProps({
  label: {
    type: String,
    required: true
  },
  value: {
    type: [Number, String, null],
    default: null
  },
  status: {
    type: String,
    default: 'gray'
  }
})

/* Format the displayed value */
const displayValue = computed(() => {
  if (props.value === null || props.value === undefined) return '—'

  // If numeric, format to 2 decimals
  if (typeof props.value === 'number') {
    return props.value.toFixed(2)
  }

  return props.value
})

/* Tile color based on backend status */
const statusClass = computed(() => {
  switch (props.status) {
    case 'green':
      return 'bg-green-200 border border-green-400'
    case 'yellow':
      return 'bg-yellow-200 border border-yellow-400'
    case 'orange':
      return 'bg-orange-200 border border-orange-400'
    case 'red':
      return 'bg-red-200 border border-red-400'
    default:
      return 'bg-gray-200 border border-gray-400'
  }
})
</script>

<style scoped>
/* Optional: tweak tile sizing or hover effects here */
</style>

