import { ref, onMounted } from 'vue'

// ⭐ Add this at the top-level (same indentation as export function)
function cToF(c: number) {
  return (c * 9) / 5 + 32
}

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

      // ⭐ Your indentation here is correct
      system.value = {
        ...json,
        temperature_f: json.temperature_c != null ? cToF(json.temperature_c) : null
      }

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

  return { system, loading, error, loadSystem }
}
