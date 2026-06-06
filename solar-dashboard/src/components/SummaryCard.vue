<template>
  <div class="p-4 bg-gray-800 rounded-lg shadow text-center">
    <h2 class="text-sm text-gray-400">{{ title }}</h2>
    <p class="text-2xl font-bold text-blue-300">{{ value }} kWh</p>
  </div>
</template>

<script setup lang="ts">
defineProps({
  title: String,
  value: Number
})
</script>
