import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig({
  base: '/',   // ⭐ REQUIRED FOR PRODUCTION ⭐
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    host: true,          // ⭐ THIS exposes Vite to your LAN ⭐
    port: 5173,          // optional but recommended
    allowedHosts: ['pvs6-pi.taildcc9dd.ts.net'],
    proxy: {
      '/api': {
        target: 'https://pvs6-pi.taildcc9dd.ts.net:8444',
        changeOrigin: true,
        secure: false
      }
    }
  }
})
