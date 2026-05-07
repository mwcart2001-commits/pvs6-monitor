import { ref, onMounted } from 'vue'

export function useSystemSnapshot() {
  console.log('🔥 CurrentSystemPage.vue is running')
  console.log('useSystemSnapshot() called')  
  const system = ref(null)
  const loading = ref(true)
  const error = ref<string | null>(null)

  async function loadSystem() {
    loading.value = true
    error.value = null

    try {
      const res = await fetch('/api/system/current')
      console.log('SYSTEM FETCH STATUS:', res.status)

      if (!res.ok) throw new Error(`HTTP ${res.status}`)

      const json = await res.json()
      console.log('SYSTEM FETCH JSON:', json)

      system.value = json
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

  // ⬅️ THIS MUST BE OUTSIDE loadSystem()
  onMounted(loadSystem)

  // ⬅️ THIS MUST ALSO BE OUTSIDE loadSystem()
  return { system, loading, error, loadSystem }
}
