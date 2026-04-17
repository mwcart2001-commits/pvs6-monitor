<template>
  <div class="p-4 bg-white shadow rounded w-full">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-semibold">Hourly Energy (kWh)</h2>

      <input
        type="date"
        v-model="selectedDate"
        @change="loadData"
        class="border rounded px-2 py-1 text-sm"
      />
    </div>

    <div style="height: 380px;">
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

async function fetchHourly(date) {
  const url = `http://192.168.1.225:8000/api/history/day/hourly?date=${date}`;
  const res = await fetch(url);
  return await res.json();
}

async function loadData() {
  const data = await fetchHourly(selectedDate.value);

  const labels = data.hours;
  const prod = data.production_kwh;
  const cons = data.consumption_kwh;
  const net = data.net_kwh;

  if (chart) chart.destroy();

  chart = new Chart(canvas.value.getContext("2d"), {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Production (kWh)",
          data: prod,
          backgroundColor: "rgba(34, 197, 94, 0.6)",
          borderColor: "#22c55e",
          borderWidth: 1
        },
        {
          label: "Consumption (kWh)",
          data: cons,
          backgroundColor: "rgba(59, 130, 246, 0.6)",
          borderColor: "#3b82f6",
          borderWidth: 1
        },
        {
          label: "Net (kWh)",
          data: net,
          type: "line",
          borderColor: "#f97316",
          backgroundColor: "rgba(249, 115, 22, 0.2)",
          borderWidth: 3,
          tension: 0.25,
          yAxisID: "y"
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          title: { display: true, text: "kWh" }
        }
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
