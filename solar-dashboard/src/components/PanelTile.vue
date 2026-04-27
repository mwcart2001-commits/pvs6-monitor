<template>
  <div
    class="panel-tile flex items-center justify-center border rounded-md h-20 w-20 bg-gray-100"
  >
    {{ label }}
  </div>
</template>

<script setup>
defineProps({
  label: String
})
</script>
