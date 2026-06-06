<template>
  <div class="grid grid-cols-2 gap-4">
    <div class="p-4 bg-gray-800 rounded-lg shadow">
      <h2 class="text-sm text-gray-400">Solar Generation</h2>
      <p class="text-2xl font-bold text-green-400">{{ current.production_kw }} kW</p>
    </div>

    <div class="p-4 bg-gray-800 rounded-lg shadow">
      <h2 class="text-sm text-gray-400">Home Load</h2>
      <p class="text-2xl font-bold text-yellow-400">{{ current.consumption_kw }} kW</p>
    </div>

    <div class="p-4 bg-gray-800 rounded-lg shadow">
      <h2 class="text-sm text-gray-400">Net Power</h2>
      <p class="text-2xl font-bold" :class="netColor">
        {{ current.net_kw }} kW
      </p>
    </div>

    <div class="p-4 bg-gray-800 rounded-lg shadow">
      <h2 class="text-sm text-gray-400">Grid Import</h2>
      <p class="text-2xl font-bold text-blue-400">{{ current.grid_kw }} kW</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const current = ref({
  production_kw: 0,
  consumption_kw: 0,
  net_kw: 0,
  grid_kw: 0
})

const netColor = computed(() =>
  current.value.net_kw >= 0 ? "text-green-400" : "text-red-400"
)

async function loadCurrent() {
  const res = await fetch("/api/current")
  current.value = await res.json()
}

onMounted(() => {
  loadCurrent()
  setInterval(loadCurrent, 5000)
})
</script>
