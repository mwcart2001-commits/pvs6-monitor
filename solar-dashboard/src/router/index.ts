import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

import DashboardPage from '../pages/DashboardPage.vue'
import CurrentSystemPage from '../pages/CurrentSystemPage.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Dashboard',
    component: DashboardPage
  },
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

