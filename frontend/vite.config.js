// frontend/vite.config.js
import { fileURLToPath, URL } from 'node:url' // Убедитесь, что эти импорты есть

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
  ],
  resolve: {
    alias: {
      // >>>>> ВОТ ЭТА СТРОКА ВАЖНА <<<<<
      '@': fileURLToPath(new URL('./src', import.meta.url))
      // >>>>> КОНЕЦ ВАЖНОЙ СТРОКИ <<<<<

      // Могут быть и другие алиасы
    }
  },
  // Другие настройки Vite...
})