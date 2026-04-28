<script setup>
import { ref, onMounted } from 'vue'
import SystemSummaryCard from '../components/SystemSummaryCard.vue'
import PanelGrid from '../components/PanelGrid.vue'

const loading = ref(true)
const error = ref(null)

const solar = ref(0)
const load = ref(0)
const net = ref(0)
const grid = ref(0)

onMounted(async () => {
  try {
    const res = await fetch('/api/system/current')
    if (!res.ok) throw new Error('Failed to fetch system snapshot')

    const data = await res.json()

    solar.value = data.solar_kw ?? 0
    load.value = data.load_kw ?? 0
    net.value = data.net_kw ?? 0
    grid.value = data.grid_kw ?? 0
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
})
</script>
