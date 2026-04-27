import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import CurrentSystemPage from '../pages/CurrentSystemPage.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/current-system',
    name: 'CurrentSystem',
    component: CurrentSystemPage
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router

