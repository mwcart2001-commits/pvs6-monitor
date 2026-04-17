<template>
  <div class="p-4 bg-white shadow rounded w-full">

    <!-- Header -->
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-semibold">Daily Energy</h2>

      <input
        type="date"
        v-model="selectedDate"
        @change="loadData"
        class="border rounded px-2 py-1 text-sm"
      />
    </div>

    <!-- Chart Container (MUST be outside the header) -->
    <div class="chart-container">
      <canvas ref="canvas"></canvas>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import Chart from "chart.js/auto";

const canvas = ref(null);
let chart = null;

const selectedDate = ref(new Date().toISOString().slice(0, 10));

async function fetchDay(date) {
  const url = `http://192.168.1.225:8000/api/history/day?date=${date}`;
  const res = await fetch(url);
  return await res.json();
}

async function loadData() {
  const data = await fetchDay(selectedDate.value);

  const labels = data.timestamps.map(ts =>
    new Date(ts * 1000).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit"
    })
  );

  const datasets = [
    {
      label: "Production (kW)",
      data: data.production,
      borderColor: "#22c55e",
      backgroundColor: "rgba(34, 197, 94, 0.2)",
      tension: 0.25
    },
    {
      label: "Consumption (kW)",
      data: data.consumption,
      borderColor: "#3b82f6",
      backgroundColor: "rgba(59, 130, 246, 0.2)",
      tension: 0.25
    },
    {
      label: "Grid (kW)",
      data: data.grid,
      borderColor: "#ef4444",
      backgroundColor: "rgba(239, 68, 68, 0.2)",
      tension: 0.25
    }
  ];

  if (chart) chart.destroy();

  chart = new Chart(canvas.value.getContext("2d"), {
    type: "line",
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { beginAtZero: true }
      },
      interaction: {
        mode: "index",
        intersect: false
      }
    }
  });
}

onMounted(loadData);
</script>

<style scoped>
.chart-container {
  height: 350px;
  position: relative; /* REQUIRED for Chart.js */
}
</style>

