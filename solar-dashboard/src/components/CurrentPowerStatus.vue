<template>
  <div class="grid grid-cols-4 gap-4">
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
import { ref, onMounted, computed } from 'vue'

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
  const data = await res.json()

  // ⭐ Store rounded values directly
  current.value = {
    production_kw: Number(data.production_kw.toFixed(2)),
    consumption_kw: Number(data.consumption_kw.toFixed(2)),
    grid_kw: Number(data.grid_kw.toFixed(2)),
    net_kw: Number(data.grid_kw.toFixed(2)) // using grid_kw as net power
  }
}

onMounted(() => {
  loadCurrent()
  setInterval(loadCurrent, 5000)
})
</script>
