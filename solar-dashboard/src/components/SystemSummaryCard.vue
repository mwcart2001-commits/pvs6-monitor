<template>
  <div class="p-4 rounded-lg shadow bg-white flex flex-col gap-1 w-40">
    <div class="text-sm text-gray-500">{{ label }}</div>
    <div class="text-2xl font-semibold">{{ value }}</div>
    <div v-if="unit" class="text-sm text-gray-400">{{ unit }}</div>
  </div>
</template>

<script setup>
defineProps({
  label: String,
  value: [String, Number],
  unit: String
})
</script>
