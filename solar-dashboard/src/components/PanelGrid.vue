<template>
  <div class="space-y-4">

    <!-- Row 1: 8 panels -->
    <div class="flex gap-2">
      <PanelTile v-for="p in row1" :key="p" :label="p" />
    </div>

    <!-- Row 2: 7 panels -->
    <div class="flex gap-2">
      <PanelTile v-for="p in row2" :key="p" :label="p" />
    </div>

  </div>
</template>

<script setup>
import PanelTile from './PanelTile.vue'

const row1 = ['R1C1','R1C2','R1C3','R1C4','R1C5','R1C6','R1C7','R1C8']
const row2 = ['R2C1','R2C2','R2C3','R2C4','R2C5','R2C6','R2C7']
</script>
