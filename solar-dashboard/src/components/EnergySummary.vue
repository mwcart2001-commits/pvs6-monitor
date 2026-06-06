<template>
  <div class="grid grid-cols-4 gap-4 mt-6">
    <SummaryCard title="Today" :value="summary.today" />
    <SummaryCard title="This Week" :value="summary.week" />
    <SummaryCard title="This Month" :value="summary.month" />
    <SummaryCard title="This Year" :value="summary.year" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import SummaryCard from './SummaryCard.vue'

const summary = ref({
  today: 0,
  week: 0,
  month: 0,
  year: 0
})

async function loadSummary() {
  const res = await fetch("/api/summary/all")
  summary.value = await res.json()
}

onMounted(() => {
  loadSummary()
})
</script>
