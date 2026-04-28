import { ref, onMounted } from 'vue'

export function useSystemSnapshot() {
  const data = ref(null)
  const loading = ref(true)
  const error = ref(null)

  async function fetchSnapshot() {
    loading.value = true
    error.value = null

    try {
      const res = await fetch('/api/system/current')
      if (!res.ok) throw new Error('Failed to fetch system snapshot')

      data.value = await res.json()
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  onMounted(() => {
    fetchSnapshot()
  })

  return {
    data,
    loading,
    error,
    refresh: fetchSnapshot
  }
}
