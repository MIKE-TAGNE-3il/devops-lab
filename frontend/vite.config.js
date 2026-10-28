import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    // Uniquement pour "npm run dev" : relaie /api vers le backend publié sur 127.0.0.1:8000.
    // En conteneur, c'est Nginx (puis Traefik en production) qui joue ce rôle.
    proxy: { '/api': 'http://127.0.0.1:8000' },
  },
})
