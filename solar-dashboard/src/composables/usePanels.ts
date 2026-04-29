import { ref, onMounted } from 'vue'

export function usePanels() {
  const panels = ref([])
  const loading = ref(true)
  const error = ref(null)

  async function loadPanels() {
    loading.value = true
    error.value = null

    try {
      const res = await fetch('/api/panels')
      if (!res.ok) throw new Error(`HTTP ${res.status}`)

      const data = await res.json()

      // Sort by physical label (R1C1 → R2C7)
      data.sort((a, b) => a.physical_label.localeCompare(b.physical_label))

      panels.value = data
    } catch (err) {
      error.value = err
    } finally {
      loading.value = false
    }
  }

  onMounted(loadPanels)

  return {
    panels,
    loading,
    error,
    reload: loadPanels
  }
}
