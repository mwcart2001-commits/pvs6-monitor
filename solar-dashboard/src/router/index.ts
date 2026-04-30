import { createRouter, createWebHistory } from 'vue-router'
import DashboardPage from '../pages/DashboardPage.vue'
import CurrentSystemPage from '../pages/CurrentSystemPage.vue'

const routes = [
  { path: '/', component: DashboardPage },
  { path: '/current-system', component: CurrentSystemPage }
]

export default createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})
