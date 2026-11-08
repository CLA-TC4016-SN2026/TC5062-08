import react from '@vitejs/plugin-react'
import { loadEnv } from 'vite'
import { defineConfig } from 'vitest/config'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  return {
    plugins: [react()],
    test: {
      environment: 'node',
      include: ['src/**/*.test.ts'],
      // En Node no hay origen de página, así que la URL base de la API debe ser absoluta.
      // Con BACKEND_URL se ejecutan también las pruebas de integración contra un backend real.
      env: {
        VITE_API_URL: process.env.BACKEND_URL ?? 'http://localhost:8000/api/v1',
        VITE_RUN_INTEGRATION: process.env.BACKEND_URL ? '1' : '',
      },
    },
    server: {
      // En desarrollo las peticiones a /api van al backend: evita CORS.
      proxy: {
        '/api': {
          target: env.VITE_PROXY_TARGET || 'http://localhost:8000',
          changeOrigin: true,
        },
      },
    },
  }
})
