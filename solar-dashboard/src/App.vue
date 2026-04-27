<script setup>
import { ref, onMounted } from "vue";
import DailyChart from "./components/DailyChart.vue";
import DailyHourlyChart from "./components/DailyHourlyChart.vue";

const view = ref("power");

// ⭐ Mode indicator state
const mode = ref("unknown");

// ⭐ Fetch mode from backend
onMounted(async () => {
  try {
    const res = await fetch("/mode");
    const data = await res.json();
    mode.value = data.mode;
  } catch {
    mode.value = "unknown";
  }
});
</script>

// Commenting out this entire older section for now

<template>
  <!--
  <div class="mode-badge" :class="mode">
    {{ mode.toUpperCase() }} MODE
  </div>

  <div class="p-6 space-y-6">

    <!-- Toggle Buttons -->
    <div class="flex gap-3 mb-4">
      <button
        @click="view = 'power'"
        :class="[
          'px-4 py-2 rounded font-medium',
          view === 'power'
            ? 'bg-blue-600 text-white'
            : 'bg-gray-200 text-gray-700'
        ]"
      >
        Dynamic Power (kW)
      </button>

      <button
        @click="view = 'hourly'"
        :class="[
          'px-4 py-2 rounded font-medium',
          view === 'hourly'
            ? 'bg-blue-600 text-white'
            : 'bg-gray-200 text-gray-700'
        ]"
      >
        Hourly Energy (kWh)
      </button>
    </div>

    <!-- Chart Display -->
    <div>
      <DailyChart v-if="view === 'power'" />
      <DailyHourlyChart v-if="view === 'hourly'" />
    </div>
  </div>
  -->
  
    <router-view />
</template>

<style>
/* ⭐ Mode Badge Styles */
.mode-badge {
  position: fixed;
  top: 10px;
  right: 10px;
  padding: 4px 8px;
  font-size: 10px;
  font-weight: bold;
  border-radius: 4px;
  color: white;
  z-index: 9999;
  opacity: 0.85;
}

.mode-badge.dev {
  background: #42b883; /* Vue green */
}

.mode-badge.prod {
  background: #35495e; /* Vue dark */
}

.mode-badge.unknown {
  background: #999;
}
</style>

