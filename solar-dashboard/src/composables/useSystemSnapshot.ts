import { ref, onMounted } from 'vue'

export function useSystemSnapshot() {
  const system = ref(null)
  const loading = ref(true)
  const error = ref<string | null>(null)

  async function loadSystem() {
    loading.value = true
    error.value = null

    try {
      const res = await fetch('/api/system/current')
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      system.value = await res.json()
    } catch (err) {
      if (err instanceof Error) {
        error.value = err.message
      } else {
        error.value = String(err)
      }
    } finally {
      loading.value = false
    }
  }

  onMounted(loadSystem)

  return { system, loading, error, reload: loadSystem }
}
