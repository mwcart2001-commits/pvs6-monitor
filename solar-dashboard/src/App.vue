<script setup>
import { ref } from "vue";
import DailyChart from "./components/DailyChart.vue";
import DailyHourlyChart from "./components/DailyHourlyChart.vue";

const view = ref("power");
</script>

<template>
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
</template>
