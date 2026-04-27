import { createRouter, createWebHistory } from 'vue-router'
import CurrentSystemPage from '../pages/CurrentSystemPage.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/current-system',
      name: 'CurrentSystem',
      component: CurrentSystemPage
    }
  ],
})

export default router
