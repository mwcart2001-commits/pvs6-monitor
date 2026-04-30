<template>
  <div class="bg-gray-100 rounded-xl p-4 shadow-sm text-center">
    <div class="text-sm text-gray-600">
      {{ label }}
    </div>

    <div class="text-2xl font-semibold mt-1">
      {{ displayValue }}
      <span v-if="unit" class="text-base text-gray-500 ml-1">{{ unit }}</span>
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
  unit: {
    type: String,
    default: ''
  }
})

/* Format the displayed value */
const displayValue = computed(() => {
  if (props.value === null || props.value === undefined) return '—'

  if (typeof props.value === 'number') {
    return props.value.toFixed(2)
  }

  return props.value
})
</script>

<style scoped>
/* Optional: add hover or animation effects here */
</style>

