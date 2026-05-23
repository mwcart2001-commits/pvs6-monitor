<template>
  <div class="p-4 bg-white rounded-xl shadow space-y-4">

    <h2 class="text-xl font-semibold text-gray-800">Energy Summary</h2>

    <!-- Tabs -->
    <div class="flex gap-2">
      <button
        v-for="tab in tabs"
        :key="tab"
        @click="activeTab = tab"
        :class="[
          'px-3 py-2 rounded-lg transition',
          activeTab === tab
            ? 'bg-blue-600 text-white shadow'
            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
        ]"
      >
        {{ tab }}
      </button>
      <!-- Temporary test button -->
      <button class="bg-blue-600 text-white px-3 py-2 rounded-lg">
        Test
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-gray-500">Loading summary...</div>

    <!-- Error -->
    <div v-else-if="error" class="text-red-600">Failed to load summary.</div>

    <!-- Summary -->
    <div v-else class="grid grid-cols-2 sm:grid-cols-4 gap-4">

      <div class="p-3 bg-gray-50 rounded-lg text-center">
        <p class="text-sm text-gray-500">Solar Production</p>
        <p class="text-lg font-semibold">{{ summary.solar_kwh }} kWh</p>
      </div>

      <div class="p-3 bg-gray-50 rounded-lg text-center">
        <p class="text-sm text-gray-500">Home Consumption</p>
        <p class="text-lg font-semibold">{{ summary.load_kwh }} kWh</p>
      </div>

      <div class="p-3 bg-gray-50 rounded-lg text-center">
        <p class="text-sm text-gray-500">Grid Import</p>
        <p class="text-lg font-semibold">{{ summary.grid_import_kwh }} kWh</p>
      </div>

      <div class="p-3 bg-gray-50 rounded-lg text-center">
        <p class="text-sm text-gray-500">Net Energy</p>
        <p
          class="text-lg font-semibold"
          :class="summary.net_kwh >= 0 ? 'text-green-600' : 'text-red-600'"
        >
          {{ summary.net_kwh }} kWh
        </p>
      </div>

    </div>

  </div>
</template>

<script setup>
console.log("SystemEnergySummary script loaded")
import { ref, onMounted, watch } from 'vue'

const tabs = ['Today', 'This Week', 'This Month', 'This Year']
const activeTab = ref('Today')

const summary = ref({})
const loading = ref(false)
const error = ref(false)

function todayDate() {
  return new Date().toISOString().split('T')[0]
}
console.log('todayDate():', todayDate())

function buildEndpoint() {
  const date = todayDate()

  switch (activeTab.value) {
    case 'Today':
      return `/api/summary/daily?date=${date}`
    case 'This Week':
      return `/api/summary/weekly?date=${date}`
    case 'This Month':
      return `/api/summary/monthly?date=${date}`
    case 'This Year':
      return `/api/summary/yearly?date=${date}`
  }
}

async function fetchSummary() {
  loading.value = true
  error.value = false

  try {
    const endpoint = buildEndpoint()
    const res = await fetch(endpoint)

    if (!res.ok) throw new Error('Network error')

    const data = await res.json()

    // Map backend fields to frontend fields
    summary.value = {
      solar_kwh: data.production_kwh,
      load_kwh: data.consumption_kwh,
      grid_import_kwh: data.grid_import_kwh,
      grid_export_kwh: data.grid_export_kwh,
      net_kwh: data.net_kwh
    }

  } catch (err) {
    console.error(err)
    error.value = true
  } finally {
    loading.value = false
  }
}

onMounted(fetchSummary)

watch(activeTab, () => {
  console.log("ACTIVE TAB:", activeTab.value)
  fetchSummary()
})
</script>
