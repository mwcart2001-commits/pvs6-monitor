<script setup>
import { ref, onMounted, watch } from "vue"

const tabs = ["Today", "This Week", "This Month", "This Year"]
const activeTab = ref("Today")

const loading = ref(false)
const error = ref(null)
const summary = ref(null)

function buildUrl() {
  const today = new Date()
  const yyyy = today.getFullYear()
  const mm = String(today.getMonth() + 1).padStart(2, "0")
  const dd = String(today.getDate()).padStart(2, "0")
  const dateStr = `${yyyy}-${mm}-${dd}`

  switch (activeTab.value) {
    case "Today":
      return `/api/summary/daily?date=${dateStr}`
    case "This Week":
      return `/api/summary/weekly?date=${dateStr}`
    case "This Month":
      return `/api/summary/monthly?date=${dateStr}`
    case "This Year":
      return `/api/summary/yearly?date=${yyyy}`
  }
}

async function fetchSummary() {
  loading.value = true
  error.value = null

  try {
    const url = buildUrl()
    const res = await fetch(url)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)

    const data = await res.json()

    // ⭐ Correct mapping for your backend
    summary.value = {
      energy_generated: data.production_kwh,
      energy_used: data.consumption_kwh,
      net_energy: data.net_kwh,
      grid_import: data.grid_import_kwh,
      grid_export: data.grid_export_kwh
    }
  } catch (err) {
    console.error("Failed to fetch summary:", err)
    error.value = "Failed to load summary"
  } finally {
    loading.value = false
  }
}

onMounted(fetchSummary)
watch(activeTab, fetchSummary)
</script>

<template>
  <div class="w-full">
    <!-- Tabs -->
    <div class="flex gap-2 mb-4">
      <button
        v-for="tab in tabs"
        :key="tab"
        @click="activeTab = tab"
        class="px-3 py-2 rounded-lg"
        :class="[
          activeTab === tab
            ? 'bg-blue-600 text-white'
            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
        ]"
      >
        {{ tab }}
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-gray-500">Loading...</div>

    <!-- Error -->
    <div v-if="error" class="text-red-500">{{ error }}</div>

    <!-- Summary Content -->
    <div v-if="summary" class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="p-4 bg-white rounded-lg shadow">
        <div class="text-gray-500 text-sm">Energy Generated</div>
        <div class="text-xl font-bold">{{ summary.energy_generated }} kWh</div>
      </div>

      <div class="p-4 bg-white rounded-lg shadow">
        <div class="text-gray-500 text-sm">Energy Used</div>
        <div class="text-xl font-bold">{{ summary.energy_used }} kWh</div>
      </div>

      <div class="p-4 bg-white rounded-lg shadow">
        <div class="text-gray-500 text-sm">Net Energy</div>
        <div
          class="text-xl font-bold"
          :class="summary.net_energy < 0 ? 'text-red-600' : 'text-green-600'"
        >
          {{ summary.net_energy }} kWh
        </div>
      </div>

      <div class="p-4 bg-white rounded-lg shadow">
        <div class="text-gray-500 text-sm">Grid Import / Export</div>
        <div class="text-xl font-bold">
          {{ summary.grid_import }} / {{ summary.grid_export }} kWh
        </div>
      </div>
    </div>
  </div>
</template>
