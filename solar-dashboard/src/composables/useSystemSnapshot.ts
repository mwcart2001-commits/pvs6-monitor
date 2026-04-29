import { ref, onMounted } from 'vue'

export function useSystemSnapshot() {
  const system = ref(null)
  const loading = ref(true)
  const error = ref(null)

  async function loadSystem() {
    loading.value = true
    error.value = null
    try {
      const res = await fetch('/api/system/current')
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      system.value = await res.json()
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  onMounted(loadSystem)

  return { system, loading, error, reload: loadSystem }
}
