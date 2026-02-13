import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const API_BASE = process.env.VITE_API_BASE_URL || 'https://api.meetapexneural.com'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: API_BASE.replace(/\/$/, ''),
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
